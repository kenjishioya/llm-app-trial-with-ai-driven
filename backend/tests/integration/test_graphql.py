"""
GraphQL統合テスト（モック適用版）
"""

import uuid
import pytest
from unittest.mock import patch, AsyncMock


class TestGraphQLWithMocks:
    """GraphQL統合テスト（モック使用）"""

    def test_graphql_health_query(self, client, patch_llm_service):
        """GraphQL ヘルスクエリテスト"""
        query = """
        query {
            health {
                status
                timestamp
            }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert data["data"]["health"]["status"] == "ok"
        assert "timestamp" in data["data"]["health"]

    def test_create_session_mutation(self, client, patch_llm_service):
        """セッション作成ミューテーションテスト"""
        mutation = """
        mutation {
            createSession(input: {title: "Test Session"}) {
                id
                title
                createdAt
            }
        }
        """
        response = client.post("/graphql", json={"query": mutation})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        session = data["data"]["createSession"]
        assert session["title"] == "Test Session"
        assert "id" in session
        assert "createdAt" in session

    def test_ask_mutation_with_mock(self, client, patch_llm_service):
        """質問ミューテーションテスト（モック使用）"""
        # まずセッションを作成
        session_mutation = """
        mutation {
            createSession(input: {title: "Ask Test Session"}) {
                id
            }
        }
        """
        session_response = client.post("/graphql", json={"query": session_mutation})
        session_id = session_response.json()["data"]["createSession"]["id"]

        # 質問を実行（モックLLMサービスが使用される）
        ask_mutation = f"""
        mutation {{
            ask(input: {{
                question: "Hello, how are you?"
                sessionId: "{session_id}"
                deepResearch: false
            }}) {{
                sessionId
                messageId
                stream
            }}
        }}
        """
        response = client.post("/graphql", json={"query": ask_mutation})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        ask_result = data["data"]["ask"]
        assert ask_result["sessionId"] == session_id
        assert "messageId" in ask_result
        assert "stream" in ask_result
        # streamフィールドはSSE endpoint URLを含む想定
        assert isinstance(ask_result["stream"], str)

    def test_sessions_query(self, client, patch_llm_service):
        """セッション一覧クエリテスト"""
        # テスト用セッションを作成
        mutation = """
        mutation {
            createSession(input: {title: "Query Test Session"}) {
                id
                title
            }
        }
        """
        client.post("/graphql", json={"query": mutation})

        # セッション一覧を取得
        query = """
        query {
            sessions {
                id
                title
                createdAt
                updatedAt
            }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        sessions = data["data"]["sessions"]
        assert isinstance(sessions, list)
        assert len(sessions) >= 1

        # 最新のセッションをチェック
        session = sessions[0]
        assert "id" in session
        assert "title" in session
        assert "createdAt" in session

    def test_session_by_id_query(self, client, patch_llm_service):
        """セッション詳細クエリテスト"""
        # テスト用セッションを作成
        mutation = """
        mutation {
            createSession(input: {title: "Detail Test Session"}) {
                id
            }
        }
        """
        session_response = client.post("/graphql", json={"query": mutation})
        session_id = session_response.json()["data"]["createSession"]["id"]

        # セッション詳細を取得
        query = f"""
        query {{
            session(id: "{session_id}") {{
                id
                title
                createdAt
                messages {{
                    id
                    role
                    content
                    createdAt
                }}
            }}
        }}
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        session = data["data"]["session"]
        assert session["id"] == session_id
        assert session["title"] == "Detail Test Session"
        assert "messages" in session

    def test_update_session_mutation(self, client, patch_llm_service):
        """セッション更新ミューテーションテスト"""
        # テスト用セッションを作成
        mutation = """
        mutation {
            createSession(input: {title: "Original Title"}) {
                id
            }
        }
        """
        session_response = client.post("/graphql", json={"query": mutation})
        session_id = session_response.json()["data"]["createSession"]["id"]

        # セッションを更新
        update_mutation = f"""
        mutation {{
            updateSession(id: "{session_id}", input: {{title: "Updated Title"}}) {{
                id
                title
                updatedAt
            }}
        }}
        """
        response = client.post("/graphql", json={"query": update_mutation})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        updated_session = data["data"]["updateSession"]
        assert updated_session["id"] == session_id
        assert updated_session["title"] == "Updated Title"
        assert "updatedAt" in updated_session

    def test_delete_session_mutation(self, client, patch_llm_service):
        """セッション削除ミューテーションテスト"""
        # テスト用セッションを作成
        mutation = """
        mutation {
            createSession(input: {title: "Session to Delete"}) {
                id
            }
        }
        """
        session_response = client.post("/graphql", json={"query": mutation})
        session_id = session_response.json()["data"]["createSession"]["id"]

        # セッションを削除
        delete_mutation = f"""
        mutation {{
            deleteSession(id: "{session_id}")
        }}
        """
        response = client.post("/graphql", json={"query": delete_mutation})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert data["data"]["deleteSession"] is True

        # 削除確認
        query = f"""
        query {{
            session(id: "{session_id}") {{
                id
            }}
        }}
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        assert data["data"]["session"] is None

    def test_invalid_session_query(self, client, patch_llm_service):
        """無効セッションクエリテスト"""
        invalid_session_id = str(uuid.uuid4())
        query = f"""
        query {{
            session(id: "{invalid_session_id}") {{
                id
                title
            }}
        }}
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert data["data"]["session"] is None

    @pytest.mark.asyncio
    async def test_graphql_schema_introspection(self, client, patch_llm_service):
        """GraphQLスキーマのイントロスペクションテスト"""
        query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                }
            }
        }
        """

        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "__schema" in data["data"]

        # 型名を取得
        type_names = [t["name"] for t in data["data"]["__schema"]["types"]]

        # 基本的な型が存在することを確認
        assert "Query" in type_names
        assert "Mutation" in type_names
        assert "Subscription" in type_names
        assert "SessionType" in type_names
        assert "MessageType" in type_names
        assert "DocumentType" in type_names
        assert "SearchResultType" in type_names

    @pytest.mark.asyncio
    async def test_search_documents_query(self, client, patch_llm_service):
        """ドキュメント検索クエリのテスト"""
        query = """
        query SearchDocuments($input: SearchInput!) {
            searchDocuments(input: $input) {
                query
                totalCount
                executionTimeMs
                documents {
                    id
                    title
                    content
                    score
                    source
                    url
                    metadata {
                        fileType
                        fileSize
                        createdAt
                        chunkIndex
                        chunkCount
                    }
                }
            }
        }
        """

        variables = {"input": {"query": "テスト検索", "topK": 5}}

        # RAGServiceのモック設定
        with patch("services.rag_service.RAGService") as mock_rag_service:
            mock_instance = mock_rag_service.return_value
            mock_instance.search_documents = AsyncMock(
                return_value=[
                    {
                        "id": "doc1",
                        "title": "テストドキュメント",
                        "content": "テスト内容",
                        "score": 0.85,
                        "source": "test.pdf",
                        "url": "https://example.com/test.pdf",
                        "metadata": {
                            "file_type": "pdf",
                            "file_size": 1024,
                            "created_at": "2025-06-12T00:00:00Z",
                            "chunk_index": 0,
                            "chunk_count": 1,
                        },
                    }
                ]
            )

            response = client.post(
                "/graphql", json={"query": query, "variables": variables}
            )
            assert response.status_code == 200

            data = response.json()
            assert "data" in data
            assert "searchDocuments" in data["data"]

            search_result = data["data"]["searchDocuments"]
            assert search_result["query"] == "テスト検索"
            assert search_result["totalCount"] == 1
            assert len(search_result["documents"]) == 1

            document = search_result["documents"][0]
            assert document["id"] == "doc1"
            assert document["title"] == "テストドキュメント"
            assert document["score"] == 0.85

    @pytest.mark.asyncio
    async def test_upload_document_mutation(self, client, patch_llm_service):
        """ドキュメントアップロードミューテーションのテスト"""
        mutation = """
        mutation UploadDocument($input: UploadDocumentInput!) {
            uploadDocument(input: $input) {
                documentId
                fileName
                status
                message
                chunksCreated
            }
        }
        """

        # Base64エンコードされたテストファイル内容
        import base64

        test_content = "これはテスト用のドキュメント内容です。"
        encoded_content = base64.b64encode(test_content.encode()).decode()

        variables = {
            "input": {
                "fileName": "test.txt",
                "fileContent": encoded_content,
                "fileType": "text/plain",
                "title": "テストドキュメント",
                "metadata": '{"author": "test_user"}',
            }
        }

        # DocumentPipelineのモック設定
        with patch("services.document_pipeline.DocumentPipeline") as mock_pipeline:
            mock_instance = mock_pipeline.return_value
            mock_instance.process_document = AsyncMock(
                return_value={
                    "status": "completed",
                    "document_id": "doc123",
                    "chunks_created": 1,
                }
            )

            response = client.post(
                "/graphql", json={"query": mutation, "variables": variables}
            )
            assert response.status_code == 200

            data = response.json()
            assert "data" in data
            assert "uploadDocument" in data["data"]

            upload_result = data["data"]["uploadDocument"]
            assert upload_result["documentId"] == "doc123"
            assert upload_result["fileName"] == "test.txt"
            assert upload_result["status"] == "success"
            assert upload_result["chunksCreated"] == 1

    @pytest.mark.asyncio
    async def test_upload_document_error_handling(self, client, patch_llm_service):
        """ドキュメントアップロードのエラーハンドリングテスト"""
        mutation = """
        mutation UploadDocument($input: UploadDocumentInput!) {
            uploadDocument(input: $input) {
                documentId
                fileName
                status
                message
                chunksCreated
            }
        }
        """

        variables = {
            "input": {
                "fileName": "invalid.txt",
                "fileContent": "invalid_base64_content",  # 無効なBase64
                "fileType": "text/plain",
            }
        }

        response = client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "uploadDocument" in data["data"]

        upload_result = data["data"]["uploadDocument"]
        assert upload_result["status"] == "error"
        assert "Base64デコードエラー" in upload_result["message"]
        assert upload_result["chunksCreated"] == 0

    @pytest.mark.asyncio
    async def test_search_documents_with_filters(self, client, patch_llm_service):
        """フィルタ付きドキュメント検索のテスト"""
        query = """
        query SearchDocuments($input: SearchInput!) {
            searchDocuments(input: $input) {
                query
                totalCount
                documents {
                    id
                    title
                    metadata {
                        fileType
                    }
                }
            }
        }
        """

        variables = {
            "input": {"query": "PDF検索", "topK": 10, "filters": '{"file_type": "pdf"}'}
        }

        # RAGServiceのモック設定
        with patch("services.rag_service.RAGService") as mock_rag_service:
            mock_instance = mock_rag_service.return_value
            mock_instance.search_documents = AsyncMock(return_value=[])

            response = client.post(
                "/graphql", json={"query": query, "variables": variables}
            )
            assert response.status_code == 200

            data = response.json()
            assert "data" in data
            assert "searchDocuments" in data["data"]

            # フィルタが適切に渡されたか確認
            mock_instance.search_documents.assert_called_once()
            call_args = mock_instance.search_documents.call_args
            assert call_args[1]["filters"] == {"file_type": "pdf"}

    @pytest.mark.asyncio
    async def test_session_with_citations(self, client, patch_llm_service):
        """引用情報付きセッション取得のテスト"""
        # まずセッションを作成
        create_mutation = """
        mutation CreateSession($input: SessionInput!) {
            createSession(input: $input) {
                id
                title
            }
        }
        """

        create_variables = {"input": {"title": "引用テストセッション"}}
        create_response = client.post(
            "/graphql", json={"query": create_mutation, "variables": create_variables}
        )
        assert create_response.status_code == 200

        session_id = create_response.json()["data"]["createSession"]["id"]

        # セッション詳細取得クエリ
        query = """
        query GetSession($id: String!) {
            session(id: $id) {
                id
                title
                messages {
                    id
                    role
                    content
                    citations {
                        id
                        title
                        content
                        score
                        source
                        url
                    }
                    metaData
                }
            }
        }
        """

        variables = {"id": session_id}

        response = client.post(
            "/graphql", json={"query": query, "variables": variables}
        )
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "session" in data["data"]

        session = data["data"]["session"]
        assert session["id"] == session_id
        assert session["title"] == "引用テストセッション"
        assert isinstance(session["messages"], list)
