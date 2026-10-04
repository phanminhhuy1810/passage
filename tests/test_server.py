import unittest
from fastapi.testclient import TestClient
from server import create_app


class FakeEngine:
    metadata = {"model_name": "test", "model_revision": "test", "device": "cpu"}

    def search(self, query, method, top_k):
        return [{"document": {"id": "a", "title": "Title", "text": query}, "score": 0.5}]


class ServerChecks(unittest.TestCase):
    def setUp(self):
        data = {"documents": [{"id": "a", "title": "Title", "text": "text"}],
                "queries": [{"id": "q", "text": "Question", "gold_id": "a", "split": "dev"}]}
        self.client = TestClient(create_app(provided_engine=FakeEngine(), provided_data=data))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def test_validation_and_three_real_method_calls(self):
        for body in ({"query": "!!!"}, {"query": " "}, {"query": "a" * 501},
                     {"query": "toán", "top_k": 0}, {"query": "toán", "top_k": 6}):
            response = self.client.post("/api/search", json=body)
            self.assertEqual(response.status_code, 422)
            self.assertIn("error", response.json())
        response = self.client.post("/api/search", json={"query": "  toán  ", "top_k": 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["query"], "toán")
        self.assertEqual([r["method"] for r in response.json()["results"]],
                         ["overlap", "tfidf", "semantic"])

    def test_health_and_no_local_file_exposure(self):
        response = self.client.get("/api/status")
        self.assertTrue(response.json()["ready"])
        self.assertEqual(response.json()["app"], "vietnamese-retrieval-lab")
        self.assertEqual(response.json()["examples"], [{"text": "Question", "title": "Title"}])
        self.assertEqual(self.client.get("/dataset.py").status_code, 404)


if __name__ == "__main__":
    unittest.main()
