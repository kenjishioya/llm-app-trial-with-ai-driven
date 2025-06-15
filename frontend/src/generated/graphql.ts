import { gql } from "@apollo/client";
import * as Apollo from "@apollo/client";
import * as ApolloReactHooks from "@apollo/client";
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = {
  [K in keyof T]: T[K];
};
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]?: Maybe<T[SubKey]>;
};
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & {
  [SubKey in K]: Maybe<T[SubKey]>;
};
export type MakeEmpty<
  T extends { [key: string]: unknown },
  K extends keyof T,
> = { [_ in K]?: never };
export type Incremental<T> =
  | T
  | {
      [P in keyof T]?: P extends " $fragmentName" | "__typename" ? T[P] : never;
    };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string };
  String: { input: string; output: string };
  Boolean: { input: boolean; output: boolean };
  Int: { input: number; output: number };
  Float: { input: number; output: number };
  JSON: { input: any; output: any };
};

export type AskInput = {
  deepResearch?: Scalars["Boolean"]["input"];
  question: Scalars["String"]["input"];
  sessionId?: InputMaybe<Scalars["ID"]["input"]>;
};

export type AskPayload = {
  __typename?: "AskPayload";
  messageId: Scalars["ID"]["output"];
  sessionId: Scalars["ID"]["output"];
  stream: Scalars["String"]["output"];
};

export type CitationType = {
  __typename?: "CitationType";
  content: Scalars["String"]["output"];
  id: Scalars["Int"]["output"];
  score: Scalars["Float"]["output"];
  source: Scalars["String"]["output"];
  title: Scalars["String"]["output"];
  url: Scalars["String"]["output"];
};

export type DeepResearchInput = {
  question: Scalars["String"]["input"];
  sessionId: Scalars["String"]["input"];
};

export type DeepResearchPayload = {
  __typename?: "DeepResearchPayload";
  message?: Maybe<Scalars["String"]["output"]>;
  researchId: Scalars["String"]["output"];
  sessionId: Scalars["String"]["output"];
  status: Scalars["String"]["output"];
  streamUrl: Scalars["String"]["output"];
};

export type DeepResearchProgress = {
  __typename?: "DeepResearchProgress";
  content: Scalars["String"]["output"];
  currentNode: Scalars["String"]["output"];
  isComplete: Scalars["Boolean"]["output"];
  progressPercentage: Scalars["Int"]["output"];
  researchId: Scalars["String"]["output"];
  sessionId: Scalars["String"]["output"];
};

export type DocumentMetadataType = {
  __typename?: "DocumentMetadataType";
  chunkCount: Scalars["Int"]["output"];
  chunkIndex: Scalars["Int"]["output"];
  createdAt: Scalars["String"]["output"];
  fileSize: Scalars["Int"]["output"];
  fileType: Scalars["String"]["output"];
};

export type DocumentType = {
  __typename?: "DocumentType";
  content: Scalars["String"]["output"];
  id: Scalars["String"]["output"];
  metadata: DocumentMetadataType;
  score: Scalars["Float"]["output"];
  source: Scalars["String"]["output"];
  title: Scalars["String"]["output"];
  url: Scalars["String"]["output"];
};

export type HealthType = {
  __typename?: "HealthType";
  status: Scalars["String"]["output"];
  timestamp: Scalars["String"]["output"];
};

export enum MessageRole {
  Assistant = "ASSISTANT",
  User = "USER",
}

export type MessageType = {
  __typename?: "MessageType";
  citations: Array<CitationType>;
  content: Scalars["String"]["output"];
  createdAt: Scalars["String"]["output"];
  id: Scalars["ID"]["output"];
  metaData: Scalars["JSON"]["output"];
  role: MessageRole;
  sessionId: Scalars["ID"]["output"];
};

export type Mutation = {
  __typename?: "Mutation";
  ask: AskPayload;
  createSession: SessionType;
  deepResearch: DeepResearchPayload;
  deleteMultipleSessions: Scalars["Int"]["output"];
  deleteSession: Scalars["Boolean"]["output"];
  updateSession?: Maybe<SessionType>;
  updateSessionTitle?: Maybe<SessionType>;
  uploadDocument: UploadDocumentPayload;
};

export type MutationAskArgs = {
  input: AskInput;
};

export type MutationCreateSessionArgs = {
  input: SessionInput;
};

export type MutationDeepResearchArgs = {
  input: DeepResearchInput;
};

export type MutationDeleteMultipleSessionsArgs = {
  ids: Array<Scalars["String"]["input"]>;
};

export type MutationDeleteSessionArgs = {
  id: Scalars["String"]["input"];
};

export type MutationUpdateSessionArgs = {
  id: Scalars["String"]["input"];
  input: SessionInput;
};

export type MutationUpdateSessionTitleArgs = {
  id: Scalars["String"]["input"];
  input: UpdateSessionTitleInput;
};

export type MutationUploadDocumentArgs = {
  input: UploadDocumentInput;
};

export type Query = {
  __typename?: "Query";
  health: HealthType;
  searchDocuments: SearchResultType;
  searchSessions: Array<SessionType>;
  session?: Maybe<SessionType>;
  sessions: Array<SessionType>;
  sessionsFiltered: SessionListResult;
};

export type QuerySearchDocumentsArgs = {
  input: SearchInput;
};

export type QuerySearchSessionsArgs = {
  limit?: Scalars["Int"]["input"];
  query: Scalars["String"]["input"];
};

export type QuerySessionArgs = {
  id: Scalars["String"]["input"];
};

export type QuerySessionsArgs = {
  includeMessages?: Scalars["Boolean"]["input"];
};

export type QuerySessionsFilteredArgs = {
  input: SessionListInput;
};

export type SearchInput = {
  filters?: InputMaybe<Scalars["String"]["input"]>;
  query: Scalars["String"]["input"];
  topK?: InputMaybe<Scalars["Int"]["input"]>;
};

export type SearchResultType = {
  __typename?: "SearchResultType";
  documents: Array<DocumentType>;
  executionTimeMs: Scalars["Int"]["output"];
  query: Scalars["String"]["output"];
  totalCount: Scalars["Int"]["output"];
};

export type SessionFilterInput = {
  createdAfter?: InputMaybe<Scalars["String"]["input"]>;
  createdBefore?: InputMaybe<Scalars["String"]["input"]>;
  hasMessages?: InputMaybe<Scalars["Boolean"]["input"]>;
  searchQuery?: InputMaybe<Scalars["String"]["input"]>;
};

export type SessionInput = {
  title?: Scalars["String"]["input"];
};

export type SessionListInput = {
  filter?: InputMaybe<SessionFilterInput>;
  includeMessages?: Scalars["Boolean"]["input"];
  limit?: InputMaybe<Scalars["Int"]["input"]>;
  offset?: InputMaybe<Scalars["Int"]["input"]>;
  sort?: InputMaybe<SessionSortInput>;
};

export type SessionListResult = {
  __typename?: "SessionListResult";
  hasMore: Scalars["Boolean"]["output"];
  sessions: Array<SessionType>;
  totalCount: Scalars["Int"]["output"];
};

export enum SessionSortField {
  CreatedAt = "CREATED_AT",
  Title = "TITLE",
  UpdatedAt = "UPDATED_AT",
}

export type SessionSortInput = {
  field?: SessionSortField;
  order?: SortOrder;
};

export type SessionType = {
  __typename?: "SessionType";
  createdAt: Scalars["String"]["output"];
  id: Scalars["String"]["output"];
  messages: Array<MessageType>;
  title: Scalars["String"]["output"];
  updatedAt?: Maybe<Scalars["String"]["output"]>;
};

export enum SortOrder {
  Asc = "ASC",
  Desc = "DESC",
}

export type StreamChunk = {
  __typename?: "StreamChunk";
  content: Scalars["String"]["output"];
  isComplete: Scalars["Boolean"]["output"];
  messageId: Scalars["String"]["output"];
  sessionId: Scalars["String"]["output"];
};

export type Subscription = {
  __typename?: "Subscription";
  streamAnswer: StreamChunk;
  streamDeepResearch: DeepResearchProgress;
};

export type SubscriptionStreamAnswerArgs = {
  deepResearch?: Scalars["Boolean"]["input"];
  question: Scalars["String"]["input"];
  sessionId?: InputMaybe<Scalars["String"]["input"]>;
};

export type SubscriptionStreamDeepResearchArgs = {
  question: Scalars["String"]["input"];
  researchId: Scalars["String"]["input"];
  sessionId: Scalars["String"]["input"];
};

export type UpdateSessionTitleInput = {
  title: Scalars["String"]["input"];
};

export type UploadDocumentInput = {
  fileContent: Scalars["String"]["input"];
  fileName: Scalars["String"]["input"];
  fileType: Scalars["String"]["input"];
  metadata?: InputMaybe<Scalars["String"]["input"]>;
  title?: InputMaybe<Scalars["String"]["input"]>;
};

export type UploadDocumentPayload = {
  __typename?: "UploadDocumentPayload";
  chunksCreated: Scalars["Int"]["output"];
  documentId: Scalars["String"]["output"];
  fileName: Scalars["String"]["output"];
  message: Scalars["String"]["output"];
  status: Scalars["String"]["output"];
};

export type CreateSessionMutationVariables = Exact<{
  input: SessionInput;
}>;

export type CreateSessionMutation = {
  __typename?: "Mutation";
  createSession: {
    __typename?: "SessionType";
    id: string;
    title: string;
    createdAt: string;
    updatedAt?: string | null;
  };
};

export type AskMutationVariables = Exact<{
  input: AskInput;
}>;

export type AskMutation = {
  __typename?: "Mutation";
  ask: {
    __typename?: "AskPayload";
    sessionId: string;
    messageId: string;
    stream: string;
  };
};

export type GetSessionQueryVariables = Exact<{
  id: Scalars["String"]["input"];
}>;

export type GetSessionQuery = {
  __typename?: "Query";
  session?: {
    __typename?: "SessionType";
    id: string;
    title: string;
    createdAt: string;
    updatedAt?: string | null;
    messages: Array<{
      __typename?: "MessageType";
      id: string;
      role: MessageRole;
      content: string;
      createdAt: string;
    }>;
  } | null;
};

export type GetSessionsQueryVariables = Exact<{
  includeMessages?: InputMaybe<Scalars["Boolean"]["input"]>;
}>;

export type GetSessionsQuery = {
  __typename?: "Query";
  sessions: Array<{
    __typename?: "SessionType";
    id: string;
    title: string;
    createdAt: string;
    updatedAt?: string | null;
    messages: Array<{
      __typename?: "MessageType";
      id: string;
      content: string;
    }>;
  }>;
};

export type GetSessionsFilteredQueryVariables = Exact<{
  input: SessionListInput;
}>;

export type GetSessionsFilteredQuery = {
  __typename?: "Query";
  sessionsFiltered: {
    __typename?: "SessionListResult";
    totalCount: number;
    hasMore: boolean;
    sessions: Array<{
      __typename?: "SessionType";
      id: string;
      title: string;
      createdAt: string;
      updatedAt?: string | null;
      messages: Array<{
        __typename?: "MessageType";
        id: string;
        content: string;
        createdAt: string;
      }>;
    }>;
  };
};

export type SearchSessionsQueryVariables = Exact<{
  query: Scalars["String"]["input"];
  limit?: InputMaybe<Scalars["Int"]["input"]>;
}>;

export type SearchSessionsQuery = {
  __typename?: "Query";
  searchSessions: Array<{
    __typename?: "SessionType";
    id: string;
    title: string;
    createdAt: string;
    updatedAt?: string | null;
  }>;
};

export type HealthQueryVariables = Exact<{ [key: string]: never }>;

export type HealthQuery = {
  __typename?: "Query";
  health: { __typename?: "HealthType"; status: string; timestamp: string };
};

export type UpdateSessionMutationVariables = Exact<{
  id: Scalars["String"]["input"];
  input: SessionInput;
}>;

export type UpdateSessionMutation = {
  __typename?: "Mutation";
  updateSession?: {
    __typename?: "SessionType";
    id: string;
    title: string;
    updatedAt?: string | null;
  } | null;
};

export type UpdateSessionTitleMutationVariables = Exact<{
  id: Scalars["String"]["input"];
  input: UpdateSessionTitleInput;
}>;

export type UpdateSessionTitleMutation = {
  __typename?: "Mutation";
  updateSessionTitle?: {
    __typename?: "SessionType";
    id: string;
    title: string;
    updatedAt?: string | null;
  } | null;
};

export type DeleteSessionMutationVariables = Exact<{
  id: Scalars["String"]["input"];
}>;

export type DeleteSessionMutation = {
  __typename?: "Mutation";
  deleteSession: boolean;
};

export type DeleteMultipleSessionsMutationVariables = Exact<{
  ids: Array<Scalars["String"]["input"]> | Scalars["String"]["input"];
}>;

export type DeleteMultipleSessionsMutation = {
  __typename?: "Mutation";
  deleteMultipleSessions: number;
};

export type DeepResearchMutationVariables = Exact<{
  input: DeepResearchInput;
}>;

export type DeepResearchMutation = {
  __typename?: "Mutation";
  deepResearch: {
    __typename?: "DeepResearchPayload";
    researchId: string;
    sessionId: string;
    status: string;
    streamUrl: string;
    message?: string | null;
  };
};

export type StreamDeepResearchSubscriptionVariables = Exact<{
  researchId: Scalars["String"]["input"];
  sessionId: Scalars["String"]["input"];
  question: Scalars["String"]["input"];
}>;

export type StreamDeepResearchSubscription = {
  __typename?: "Subscription";
  streamDeepResearch: {
    __typename?: "DeepResearchProgress";
    researchId: string;
    sessionId: string;
    currentNode: string;
    progressPercentage: number;
    content: string;
    isComplete: boolean;
  };
};

export const CreateSessionDocument = gql`
  mutation CreateSession($input: SessionInput!) {
    createSession(input: $input) {
      id
      title
      createdAt
      updatedAt
    }
  }
`;
export type CreateSessionMutationFn = Apollo.MutationFunction<
  CreateSessionMutation,
  CreateSessionMutationVariables
>;

/**
 * __useCreateSessionMutation__
 *
 * To run a mutation, you first call `useCreateSessionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateSessionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createSessionMutation, { data, loading, error }] = useCreateSessionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateSessionMutation(
  baseOptions?: ApolloReactHooks.MutationHookOptions<
    CreateSessionMutation,
    CreateSessionMutationVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useMutation<
    CreateSessionMutation,
    CreateSessionMutationVariables
  >(CreateSessionDocument, options);
}
export type CreateSessionMutationHookResult = ReturnType<
  typeof useCreateSessionMutation
>;
export type CreateSessionMutationResult =
  Apollo.MutationResult<CreateSessionMutation>;
export type CreateSessionMutationOptions = Apollo.BaseMutationOptions<
  CreateSessionMutation,
  CreateSessionMutationVariables
>;
export const AskDocument = gql`
  mutation Ask($input: AskInput!) {
    ask(input: $input) {
      sessionId
      messageId
      stream
    }
  }
`;
export type AskMutationFn = Apollo.MutationFunction<
  AskMutation,
  AskMutationVariables
>;

/**
 * __useAskMutation__
 *
 * To run a mutation, you first call `useAskMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAskMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [askMutation, { data, loading, error }] = useAskMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAskMutation(
  baseOptions?: ApolloReactHooks.MutationHookOptions<
    AskMutation,
    AskMutationVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useMutation<AskMutation, AskMutationVariables>(
    AskDocument,
    options,
  );
}
export type AskMutationHookResult = ReturnType<typeof useAskMutation>;
export type AskMutationResult = Apollo.MutationResult<AskMutation>;
export type AskMutationOptions = Apollo.BaseMutationOptions<
  AskMutation,
  AskMutationVariables
>;
export const GetSessionDocument = gql`
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
 * __useGetSessionQuery__
 *
 * To run a query within a React component, call `useGetSessionQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetSessionQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetSessionQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetSessionQuery(
  baseOptions: ApolloReactHooks.QueryHookOptions<
    GetSessionQuery,
    GetSessionQueryVariables
  > &
    (
      | { variables: GetSessionQueryVariables; skip?: boolean }
      | { skip: boolean }
    ),
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useQuery<GetSessionQuery, GetSessionQueryVariables>(
    GetSessionDocument,
    options,
  );
}
export function useGetSessionLazyQuery(
  baseOptions?: ApolloReactHooks.LazyQueryHookOptions<
    GetSessionQuery,
    GetSessionQueryVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useLazyQuery<
    GetSessionQuery,
    GetSessionQueryVariables
  >(GetSessionDocument, options);
}
export function useGetSessionSuspenseQuery(
  baseOptions?:
    | ApolloReactHooks.SkipToken
    | ApolloReactHooks.SuspenseQueryHookOptions<
        GetSessionQuery,
        GetSessionQueryVariables
      >,
) {
  const options =
    baseOptions === ApolloReactHooks.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useSuspenseQuery<
    GetSessionQuery,
    GetSessionQueryVariables
  >(GetSessionDocument, options);
}
export type GetSessionQueryHookResult = ReturnType<typeof useGetSessionQuery>;
export type GetSessionLazyQueryHookResult = ReturnType<
  typeof useGetSessionLazyQuery
>;
export type GetSessionSuspenseQueryHookResult = ReturnType<
  typeof useGetSessionSuspenseQuery
>;
export type GetSessionQueryResult = Apollo.QueryResult<
  GetSessionQuery,
  GetSessionQueryVariables
>;
export const GetSessionsDocument = gql`
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
 * __useGetSessionsQuery__
 *
 * To run a query within a React component, call `useGetSessionsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetSessionsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetSessionsQuery({
 *   variables: {
 *      includeMessages: // value for 'includeMessages'
 *   },
 * });
 */
export function useGetSessionsQuery(
  baseOptions?: ApolloReactHooks.QueryHookOptions<
    GetSessionsQuery,
    GetSessionsQueryVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useQuery<GetSessionsQuery, GetSessionsQueryVariables>(
    GetSessionsDocument,
    options,
  );
}
export function useGetSessionsLazyQuery(
  baseOptions?: ApolloReactHooks.LazyQueryHookOptions<
    GetSessionsQuery,
    GetSessionsQueryVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useLazyQuery<
    GetSessionsQuery,
    GetSessionsQueryVariables
  >(GetSessionsDocument, options);
}
export function useGetSessionsSuspenseQuery(
  baseOptions?:
    | ApolloReactHooks.SkipToken
    | ApolloReactHooks.SuspenseQueryHookOptions<
        GetSessionsQuery,
        GetSessionsQueryVariables
      >,
) {
  const options =
    baseOptions === ApolloReactHooks.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useSuspenseQuery<
    GetSessionsQuery,
    GetSessionsQueryVariables
  >(GetSessionsDocument, options);
}
export type GetSessionsQueryHookResult = ReturnType<typeof useGetSessionsQuery>;
export type GetSessionsLazyQueryHookResult = ReturnType<
  typeof useGetSessionsLazyQuery
>;
export type GetSessionsSuspenseQueryHookResult = ReturnType<
  typeof useGetSessionsSuspenseQuery
>;
export type GetSessionsQueryResult = Apollo.QueryResult<
  GetSessionsQuery,
  GetSessionsQueryVariables
>;
export const GetSessionsFilteredDocument = gql`
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
 * __useGetSessionsFilteredQuery__
 *
 * To run a query within a React component, call `useGetSessionsFilteredQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetSessionsFilteredQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetSessionsFilteredQuery({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGetSessionsFilteredQuery(
  baseOptions: ApolloReactHooks.QueryHookOptions<
    GetSessionsFilteredQuery,
    GetSessionsFilteredQueryVariables
  > &
    (
      | { variables: GetSessionsFilteredQueryVariables; skip?: boolean }
      | { skip: boolean }
    ),
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useQuery<
    GetSessionsFilteredQuery,
    GetSessionsFilteredQueryVariables
  >(GetSessionsFilteredDocument, options);
}
export function useGetSessionsFilteredLazyQuery(
  baseOptions?: ApolloReactHooks.LazyQueryHookOptions<
    GetSessionsFilteredQuery,
    GetSessionsFilteredQueryVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useLazyQuery<
    GetSessionsFilteredQuery,
    GetSessionsFilteredQueryVariables
  >(GetSessionsFilteredDocument, options);
}
export function useGetSessionsFilteredSuspenseQuery(
  baseOptions?:
    | ApolloReactHooks.SkipToken
    | ApolloReactHooks.SuspenseQueryHookOptions<
        GetSessionsFilteredQuery,
        GetSessionsFilteredQueryVariables
      >,
) {
  const options =
    baseOptions === ApolloReactHooks.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useSuspenseQuery<
    GetSessionsFilteredQuery,
    GetSessionsFilteredQueryVariables
  >(GetSessionsFilteredDocument, options);
}
export type GetSessionsFilteredQueryHookResult = ReturnType<
  typeof useGetSessionsFilteredQuery
>;
export type GetSessionsFilteredLazyQueryHookResult = ReturnType<
  typeof useGetSessionsFilteredLazyQuery
>;
export type GetSessionsFilteredSuspenseQueryHookResult = ReturnType<
  typeof useGetSessionsFilteredSuspenseQuery
>;
export type GetSessionsFilteredQueryResult = Apollo.QueryResult<
  GetSessionsFilteredQuery,
  GetSessionsFilteredQueryVariables
>;
export const SearchSessionsDocument = gql`
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
 * __useSearchSessionsQuery__
 *
 * To run a query within a React component, call `useSearchSessionsQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchSessionsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchSessionsQuery({
 *   variables: {
 *      query: // value for 'query'
 *      limit: // value for 'limit'
 *   },
 * });
 */
export function useSearchSessionsQuery(
  baseOptions: ApolloReactHooks.QueryHookOptions<
    SearchSessionsQuery,
    SearchSessionsQueryVariables
  > &
    (
      | { variables: SearchSessionsQueryVariables; skip?: boolean }
      | { skip: boolean }
    ),
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useQuery<
    SearchSessionsQuery,
    SearchSessionsQueryVariables
  >(SearchSessionsDocument, options);
}
export function useSearchSessionsLazyQuery(
  baseOptions?: ApolloReactHooks.LazyQueryHookOptions<
    SearchSessionsQuery,
    SearchSessionsQueryVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useLazyQuery<
    SearchSessionsQuery,
    SearchSessionsQueryVariables
  >(SearchSessionsDocument, options);
}
export function useSearchSessionsSuspenseQuery(
  baseOptions?:
    | ApolloReactHooks.SkipToken
    | ApolloReactHooks.SuspenseQueryHookOptions<
        SearchSessionsQuery,
        SearchSessionsQueryVariables
      >,
) {
  const options =
    baseOptions === ApolloReactHooks.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useSuspenseQuery<
    SearchSessionsQuery,
    SearchSessionsQueryVariables
  >(SearchSessionsDocument, options);
}
export type SearchSessionsQueryHookResult = ReturnType<
  typeof useSearchSessionsQuery
>;
export type SearchSessionsLazyQueryHookResult = ReturnType<
  typeof useSearchSessionsLazyQuery
>;
export type SearchSessionsSuspenseQueryHookResult = ReturnType<
  typeof useSearchSessionsSuspenseQuery
>;
export type SearchSessionsQueryResult = Apollo.QueryResult<
  SearchSessionsQuery,
  SearchSessionsQueryVariables
>;
export const HealthDocument = gql`
  query Health {
    health {
      status
      timestamp
    }
  }
`;

/**
 * __useHealthQuery__
 *
 * To run a query within a React component, call `useHealthQuery` and pass it any options that fit your needs.
 * When your component renders, `useHealthQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useHealthQuery({
 *   variables: {
 *   },
 * });
 */
export function useHealthQuery(
  baseOptions?: ApolloReactHooks.QueryHookOptions<
    HealthQuery,
    HealthQueryVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useQuery<HealthQuery, HealthQueryVariables>(
    HealthDocument,
    options,
  );
}
export function useHealthLazyQuery(
  baseOptions?: ApolloReactHooks.LazyQueryHookOptions<
    HealthQuery,
    HealthQueryVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useLazyQuery<HealthQuery, HealthQueryVariables>(
    HealthDocument,
    options,
  );
}
export function useHealthSuspenseQuery(
  baseOptions?:
    | ApolloReactHooks.SkipToken
    | ApolloReactHooks.SuspenseQueryHookOptions<
        HealthQuery,
        HealthQueryVariables
      >,
) {
  const options =
    baseOptions === ApolloReactHooks.skipToken
      ? baseOptions
      : { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useSuspenseQuery<HealthQuery, HealthQueryVariables>(
    HealthDocument,
    options,
  );
}
export type HealthQueryHookResult = ReturnType<typeof useHealthQuery>;
export type HealthLazyQueryHookResult = ReturnType<typeof useHealthLazyQuery>;
export type HealthSuspenseQueryHookResult = ReturnType<
  typeof useHealthSuspenseQuery
>;
export type HealthQueryResult = Apollo.QueryResult<
  HealthQuery,
  HealthQueryVariables
>;
export const UpdateSessionDocument = gql`
  mutation UpdateSession($id: String!, $input: SessionInput!) {
    updateSession(id: $id, input: $input) {
      id
      title
      updatedAt
    }
  }
`;
export type UpdateSessionMutationFn = Apollo.MutationFunction<
  UpdateSessionMutation,
  UpdateSessionMutationVariables
>;

/**
 * __useUpdateSessionMutation__
 *
 * To run a mutation, you first call `useUpdateSessionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateSessionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateSessionMutation, { data, loading, error }] = useUpdateSessionMutation({
 *   variables: {
 *      id: // value for 'id'
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateSessionMutation(
  baseOptions?: ApolloReactHooks.MutationHookOptions<
    UpdateSessionMutation,
    UpdateSessionMutationVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useMutation<
    UpdateSessionMutation,
    UpdateSessionMutationVariables
  >(UpdateSessionDocument, options);
}
export type UpdateSessionMutationHookResult = ReturnType<
  typeof useUpdateSessionMutation
>;
export type UpdateSessionMutationResult =
  Apollo.MutationResult<UpdateSessionMutation>;
export type UpdateSessionMutationOptions = Apollo.BaseMutationOptions<
  UpdateSessionMutation,
  UpdateSessionMutationVariables
>;
export const UpdateSessionTitleDocument = gql`
  mutation UpdateSessionTitle($id: String!, $input: UpdateSessionTitleInput!) {
    updateSessionTitle(id: $id, input: $input) {
      id
      title
      updatedAt
    }
  }
`;
export type UpdateSessionTitleMutationFn = Apollo.MutationFunction<
  UpdateSessionTitleMutation,
  UpdateSessionTitleMutationVariables
>;

/**
 * __useUpdateSessionTitleMutation__
 *
 * To run a mutation, you first call `useUpdateSessionTitleMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateSessionTitleMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateSessionTitleMutation, { data, loading, error }] = useUpdateSessionTitleMutation({
 *   variables: {
 *      id: // value for 'id'
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateSessionTitleMutation(
  baseOptions?: ApolloReactHooks.MutationHookOptions<
    UpdateSessionTitleMutation,
    UpdateSessionTitleMutationVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useMutation<
    UpdateSessionTitleMutation,
    UpdateSessionTitleMutationVariables
  >(UpdateSessionTitleDocument, options);
}
export type UpdateSessionTitleMutationHookResult = ReturnType<
  typeof useUpdateSessionTitleMutation
>;
export type UpdateSessionTitleMutationResult =
  Apollo.MutationResult<UpdateSessionTitleMutation>;
export type UpdateSessionTitleMutationOptions = Apollo.BaseMutationOptions<
  UpdateSessionTitleMutation,
  UpdateSessionTitleMutationVariables
>;
export const DeleteSessionDocument = gql`
  mutation DeleteSession($id: String!) {
    deleteSession(id: $id)
  }
`;
export type DeleteSessionMutationFn = Apollo.MutationFunction<
  DeleteSessionMutation,
  DeleteSessionMutationVariables
>;

/**
 * __useDeleteSessionMutation__
 *
 * To run a mutation, you first call `useDeleteSessionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteSessionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteSessionMutation, { data, loading, error }] = useDeleteSessionMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useDeleteSessionMutation(
  baseOptions?: ApolloReactHooks.MutationHookOptions<
    DeleteSessionMutation,
    DeleteSessionMutationVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useMutation<
    DeleteSessionMutation,
    DeleteSessionMutationVariables
  >(DeleteSessionDocument, options);
}
export type DeleteSessionMutationHookResult = ReturnType<
  typeof useDeleteSessionMutation
>;
export type DeleteSessionMutationResult =
  Apollo.MutationResult<DeleteSessionMutation>;
export type DeleteSessionMutationOptions = Apollo.BaseMutationOptions<
  DeleteSessionMutation,
  DeleteSessionMutationVariables
>;
export const DeleteMultipleSessionsDocument = gql`
  mutation DeleteMultipleSessions($ids: [String!]!) {
    deleteMultipleSessions(ids: $ids)
  }
`;
export type DeleteMultipleSessionsMutationFn = Apollo.MutationFunction<
  DeleteMultipleSessionsMutation,
  DeleteMultipleSessionsMutationVariables
>;

/**
 * __useDeleteMultipleSessionsMutation__
 *
 * To run a mutation, you first call `useDeleteMultipleSessionsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteMultipleSessionsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteMultipleSessionsMutation, { data, loading, error }] = useDeleteMultipleSessionsMutation({
 *   variables: {
 *      ids: // value for 'ids'
 *   },
 * });
 */
export function useDeleteMultipleSessionsMutation(
  baseOptions?: ApolloReactHooks.MutationHookOptions<
    DeleteMultipleSessionsMutation,
    DeleteMultipleSessionsMutationVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useMutation<
    DeleteMultipleSessionsMutation,
    DeleteMultipleSessionsMutationVariables
  >(DeleteMultipleSessionsDocument, options);
}
export type DeleteMultipleSessionsMutationHookResult = ReturnType<
  typeof useDeleteMultipleSessionsMutation
>;
export type DeleteMultipleSessionsMutationResult =
  Apollo.MutationResult<DeleteMultipleSessionsMutation>;
export type DeleteMultipleSessionsMutationOptions = Apollo.BaseMutationOptions<
  DeleteMultipleSessionsMutation,
  DeleteMultipleSessionsMutationVariables
>;
export const DeepResearchDocument = gql`
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
export type DeepResearchMutationFn = Apollo.MutationFunction<
  DeepResearchMutation,
  DeepResearchMutationVariables
>;

/**
 * __useDeepResearchMutation__
 *
 * To run a mutation, you first call `useDeepResearchMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeepResearchMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deepResearchMutation, { data, loading, error }] = useDeepResearchMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeepResearchMutation(
  baseOptions?: ApolloReactHooks.MutationHookOptions<
    DeepResearchMutation,
    DeepResearchMutationVariables
  >,
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useMutation<
    DeepResearchMutation,
    DeepResearchMutationVariables
  >(DeepResearchDocument, options);
}
export type DeepResearchMutationHookResult = ReturnType<
  typeof useDeepResearchMutation
>;
export type DeepResearchMutationResult =
  Apollo.MutationResult<DeepResearchMutation>;
export type DeepResearchMutationOptions = Apollo.BaseMutationOptions<
  DeepResearchMutation,
  DeepResearchMutationVariables
>;
export const StreamDeepResearchDocument = gql`
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

/**
 * __useStreamDeepResearchSubscription__
 *
 * To run a query within a React component, call `useStreamDeepResearchSubscription` and pass it any options that fit your needs.
 * When your component renders, `useStreamDeepResearchSubscription` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the subscription, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useStreamDeepResearchSubscription({
 *   variables: {
 *      researchId: // value for 'researchId'
 *      sessionId: // value for 'sessionId'
 *      question: // value for 'question'
 *   },
 * });
 */
export function useStreamDeepResearchSubscription(
  baseOptions: ApolloReactHooks.SubscriptionHookOptions<
    StreamDeepResearchSubscription,
    StreamDeepResearchSubscriptionVariables
  > &
    (
      | { variables: StreamDeepResearchSubscriptionVariables; skip?: boolean }
      | { skip: boolean }
    ),
) {
  const options = { ...defaultOptions, ...baseOptions };
  return ApolloReactHooks.useSubscription<
    StreamDeepResearchSubscription,
    StreamDeepResearchSubscriptionVariables
  >(StreamDeepResearchDocument, options);
}
export type StreamDeepResearchSubscriptionHookResult = ReturnType<
  typeof useStreamDeepResearchSubscription
>;
export type StreamDeepResearchSubscriptionResult =
  Apollo.SubscriptionResult<StreamDeepResearchSubscription>;
