"""
GraphQL統合テスト（モック適用版）
"""

import uuid


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

    def test_graphql_schema_introspection(self, client, patch_llm_service):
        """GraphQLスキーマイントロスペクションテスト"""
        query = """
        query {
            __schema {
                types {
                    name
                }
            }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "__schema" in data["data"]
        assert "types" in data["data"]["__schema"]

        # 基本的な型が存在することを確認
        type_names = [t["name"] for t in data["data"]["__schema"]["types"]]
        assert "Query" in type_names
        assert "Mutation" in type_names
