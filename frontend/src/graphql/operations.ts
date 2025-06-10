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
 * セッション削除ミューテーション
 */
export const DELETE_SESSION = gql`
  mutation DeleteSession($id: String!) {
    deleteSession(id: $id)
  }
`;
