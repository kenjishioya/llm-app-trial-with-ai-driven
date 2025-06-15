import { gql } from "@apollo/client";

/**
 * セッション作成ミューテーション
 */
export const CREATE_SESSION = gql`
  mutation CreateSession($input: SessionInput!) {
    createSession(input: $input) {
      id
      title
      createdAt
      updatedAt
    }
  }
`;

/**
 * 質問送信ミューテーション (ask)
 */
export const ASK_MUTATION = gql`
  mutation Ask($input: AskInput!) {
    ask(input: $input) {
      sessionId
      messageId
      stream
    }
  }
`;

/**
 * セッション詳細クエリ
 */
export const GET_SESSION = gql`
  query GetSession($id: String!) {
    session(id: $id) {
      id
      title
      createdAt
      updatedAt
      messages {
        id
        role
        content
        createdAt
      }
    }
  }
`;

/**
 * セッション一覧クエリ（メッセージありなし指定可能）
 */
export const GET_SESSIONS = gql`
  query GetSessions($includeMessages: Boolean = false) {
    sessions(includeMessages: $includeMessages) {
      id
      title
      createdAt
      updatedAt
      messages {
        id
        content
      }
    }
  }
`;

/**
 * フィルタリング・ソート機能付きセッション一覧クエリ
 */
export const GET_SESSIONS_FILTERED = gql`
  query GetSessionsFiltered($input: SessionListInput!) {
    sessionsFiltered(input: $input) {
      sessions {
        id
        title
        createdAt
        updatedAt
        messages {
          id
          content
          createdAt
        }
      }
      totalCount
      hasMore
    }
  }
`;

/**
 * セッション検索クエリ
 */
export const SEARCH_SESSIONS = gql`
  query SearchSessions($query: String!, $limit: Int = 20) {
    searchSessions(query: $query, limit: $limit) {
      id
      title
      createdAt
      updatedAt
    }
  }
`;

/**
 * ヘルスチェッククエリ
 */
export const HEALTH_QUERY = gql`
  query Health {
    health {
      status
      timestamp
    }
  }
`;

/**
 * セッション更新ミューテーション
 */
export const UPDATE_SESSION = gql`
  mutation UpdateSession($id: String!, $input: SessionInput!) {
    updateSession(id: $id, input: $input) {
      id
      title
      updatedAt
    }
  }
`;

/**
 * セッションタイトル更新ミューテーション
 */
export const UPDATE_SESSION_TITLE = gql`
  mutation UpdateSessionTitle($id: String!, $input: UpdateSessionTitleInput!) {
    updateSessionTitle(id: $id, input: $input) {
      id
      title
      updatedAt
    }
  }
`;

/**
 * セッション削除ミューテーション
 */
export const DELETE_SESSION = gql`
  mutation DeleteSession($id: String!) {
    deleteSession(id: $id)
  }
`;

/**
 * 複数セッション一括削除ミューテーション
 */
export const DELETE_MULTIPLE_SESSIONS = gql`
  mutation DeleteMultipleSessions($ids: [String!]!) {
    deleteMultipleSessions(ids: $ids)
  }
`;

/**
 * Deep Research ミューテーション
 */
export const DEEP_RESEARCH_MUTATION = gql`
  mutation DeepResearch($input: DeepResearchInput!) {
    deepResearch(input: $input) {
      researchId
      sessionId
      status
      streamUrl
      message
    }
  }
`;

/**
 * Deep Research ストリーミングサブスクリプション
 */
export const STREAM_DEEP_RESEARCH_SUBSCRIPTION = gql`
  subscription StreamDeepResearch(
    $researchId: String!
    $sessionId: String!
    $question: String!
  ) {
    streamDeepResearch(
      researchId: $researchId
      sessionId: $sessionId
      question: $question
    ) {
      researchId
      sessionId
      currentNode
      progressPercentage
      content
      isComplete
    }
  }
`;
