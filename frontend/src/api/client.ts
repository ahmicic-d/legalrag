import axios from "axios";
import type {
  EvaluationQuestion,
  EvaluationResult,
  EvaluationRunResponse,
  LegalDocument,
  QueryResponse,
  SearchType,
  SeedResponse,
} from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  timeout: 180_000,
});

export async function postQuery(params: {
  question: string;
  search_type: SearchType;
  top_k: number;
}): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>("/api/query", params);
  return data;
}

export async function getDocuments(): Promise<LegalDocument[]> {
  const { data } = await api.get<LegalDocument[]>("/api/documents");
  return data;
}

export async function postSeed(): Promise<SeedResponse> {
  const { data } = await api.post<SeedResponse>("/api/ingest/seed");
  return data;
}

export async function getEvaluationQuestions(): Promise<EvaluationQuestion[]> {
  const { data } = await api.get<EvaluationQuestion[]>("/api/evaluation/questions");
  return data;
}

export async function runEvaluation(top_k = 5): Promise<EvaluationRunResponse> {
  const { data } = await api.post<EvaluationRunResponse>("/api/evaluation/run", {
    top_k,
    methods: ["keyword", "vector", "hybrid"],
  });
  return data;
}

export async function getEvaluationResults(): Promise<EvaluationResult[]> {
  const { data } = await api.get<EvaluationResult[]>("/api/evaluation/results");
  return data;
}
