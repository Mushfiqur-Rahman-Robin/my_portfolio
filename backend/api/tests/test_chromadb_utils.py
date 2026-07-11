from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from ..chromadb_utils import add_or_update_node, delete_node, get_chroma_client, get_collection, query_nodes
from ..llm_client import get_chroma_collection_name


class ChromaDBUtilsTests(TestCase):
    def test_get_chroma_collection_name_gemini(self):
        with override_settings(LLM_PROVIDER="gemini"):
            name = get_chroma_collection_name()
            self.assertIn("portfolio_knowledge", name)
            self.assertIn("gemini_embedding_2", name)

    def test_get_chroma_collection_name_openai(self):
        with override_settings(LLM_PROVIDER="openai"):
            name = get_chroma_collection_name()
            self.assertIn("portfolio_knowledge", name)
            self.assertIn("text_embedding_3_small", name)

    @patch("api.chromadb_utils.chromadb.HttpClient")
    def test_get_chroma_client(self, mock_http_client):
        client = get_chroma_client()
        mock_http_client.assert_called_once()
        self.assertEqual(client, mock_http_client.return_value)

    @patch("api.chromadb_utils.chromadb.HttpClient")
    def test_get_collection(self, mock_http_client):
        import api.chromadb_utils as chroma_mod

        mock_collection = MagicMock()
        mock_http_client.return_value.get_or_create_collection.return_value = mock_collection

        with patch.object(chroma_mod, "get_chroma_collection_name", return_value="portfolio_knowledge_test"):
            collection = get_collection()
        mock_http_client.return_value.get_or_create_collection.assert_called_once()
        self.assertEqual(collection, mock_collection)

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_add_or_update_node_success(self, mock_get_collection, mock_generate_embedding):
        mock_generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        add_or_update_node("doc-1", "sample content", {"type": "test"})

        mock_generate_embedding.assert_called_once_with("sample content", job_name=None)
        mock_collection.upsert.assert_called_once_with(
            ids=["doc-1"],
            embeddings=[[0.1, 0.2, 0.3]],
            documents=["sample content"],
            metadatas=[{"type": "test"}],
        )

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_add_or_update_node_embedding_failure(self, mock_get_collection, mock_generate_embedding):
        mock_generate_embedding.side_effect = Exception("Embedding failed")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        add_or_update_node("doc-1", "sample content", {"type": "test"})
        mock_collection.upsert.assert_not_called()

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_add_or_update_node_empty_embedding(self, mock_get_collection, mock_generate_embedding):
        mock_generate_embedding.return_value = None
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        add_or_update_node("doc-1", "sample content", {"type": "test"})
        mock_collection.upsert.assert_not_called()

    @patch("api.chromadb_utils.get_collection")
    def test_delete_node_success(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        delete_node("doc-1")
        mock_collection.delete.assert_called_once_with(ids=["doc-1"])

    @patch("api.chromadb_utils.get_collection")
    def test_delete_node_handles_missing(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.delete.side_effect = Exception("Not found")
        mock_get_collection.return_value = mock_collection

        delete_node("missing-doc")

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_query_nodes_success(self, mock_get_collection, mock_generate_embedding):
        mock_generate_embedding.return_value = [0.1, 0.2]
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10  # collection has enough docs
        mock_collection.query.return_value = {"documents": [["result1", "result2"]]}
        mock_get_collection.return_value = mock_collection

        result = query_nodes("test query")
        self.assertEqual(result["documents"], [["result1", "result2"]])
        mock_collection.query.assert_called_once()

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_query_nodes_embedding_failure(self, mock_get_collection, mock_generate_embedding):
        mock_generate_embedding.side_effect = Exception("Failed")
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_get_collection.return_value = mock_collection

        result = query_nodes("test query")
        self.assertEqual(result["documents"], [[""]])

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_query_nodes_empty_embedding(self, mock_get_collection, mock_generate_embedding):
        mock_generate_embedding.return_value = None
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_get_collection.return_value = mock_collection

        result = query_nodes("test query")
        self.assertEqual(result["documents"], [[""]])

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_query_nodes_custom_n_results(self, mock_get_collection, mock_generate_embedding):
        mock_generate_embedding.return_value = [0.1, 0.2]
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10  # collection large enough
        mock_collection.query.return_value = {"documents": [["a", "b", "c", "d", "e"]]}
        mock_get_collection.return_value = mock_collection

        result = query_nodes("test", n_results=5)
        self.assertEqual(len(result["documents"][0]), 5)

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_query_nodes_caps_n_results_to_collection_size(self, mock_get_collection, mock_generate_embedding):
        """When the collection has fewer docs than n_results, n_results is capped."""
        mock_generate_embedding.return_value = [0.1, 0.2]
        mock_collection = MagicMock()
        mock_collection.count.return_value = 3  # only 3 docs in collection
        mock_collection.query.return_value = {"documents": [["a", "b", "c"]]}
        mock_get_collection.return_value = mock_collection

        result = query_nodes("test", n_results=4)

        # query should have been called with n_results=3, not 4
        call_kwargs = mock_collection.query.call_args[1]
        self.assertEqual(call_kwargs["n_results"], 3)
        self.assertEqual(result["documents"], [["a", "b", "c"]])

    @patch("api.chromadb_utils.generate_embedding")
    @patch("api.chromadb_utils.get_collection")
    def test_query_nodes_returns_empty_when_collection_is_empty(self, mock_get_collection, mock_generate_embedding):
        """When the collection is completely empty, return early without querying."""
        mock_generate_embedding.return_value = [0.1, 0.2]
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        result = query_nodes("test query")
        self.assertEqual(result["documents"], [[""]])
        mock_collection.query.assert_not_called()
