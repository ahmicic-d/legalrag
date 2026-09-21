export type SearchType = "keyword" | "vector" | "hybrid" | "rag";
export type Confidence = "high" | "medium" | "low";

export interface Source {
  document_id: number;
  document_title: string;
  article_number: string | null;
  paragraph_number: string | null;
  source: string;
  source_url: string | null;
  document_type: string;
  legal_area: string | null;
}

export interface RetrievedChunk {
  chunk_id: number;
  document_id: number;
  document_title: string;
  article_number: string | null;
  paragraph_number: string | null;
  chunk_text: string;
  score: number;
  search_type: string;
}

export interface QueryResponse {
  question: string;
  answer: string;
  confidence: Confidence;
  search_type: SearchType;
  sources: Source[];
  retrieved_chunks: RetrievedChunk[];
  disclaimer: string;
}

export interface LegalDocument {
  id: number;
  title: string;
  source: string;
  source_url: string | null;
  document_type: string;
  legal_area: string | null;
  publication_date: string | null;
  created_at: string;
  chunk_count: number;
}

export interface EvaluationQuestion {
  id: number;
  question: string;
  expected_source: string | null;
  expected_article: string | null;
  notes: string | null;
}

export interface EvaluationResult {
  id: number;
  question_id: number;
  question: string | null;
  method: string;
  retrieved_chunk_ids: number[] | null;
  precision_at_k: number | null;
  recall_at_k: number | null;
  mrr: number | null;
  created_at: string;
}

export interface MethodSummary {
  method: string;
  avg_precision_at_k: number;
  avg_recall_at_k: number;
  avg_mrr: number;
  num_questions: number;
}

export interface EvaluationRunResponse {
  top_k: number;
  summaries: MethodSummary[];
  results: EvaluationResult[];
}

export interface SeedResponse {
  status: string;
  documents_ingested: number;
  chunks_created: number;
  details: string[];
}
