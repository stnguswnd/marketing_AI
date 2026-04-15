import { readAuthSession, type AuthSession } from "@/lib/auth";

export type LoginRequest = {
  email: string;
  password: string;
};

export type AuthSessionResponse = {
  user_id: string;
  email: string;
  display_name: string;
  role: "admin" | "merchant";
  merchant_id?: string | null;
  merchant_name?: string | null;
  profile_image_url: string;
};

export type TestAccount = {
  email: string;
  display_name: string;
  role: "admin" | "merchant";
  merchant_id?: string | null;
  merchant_name?: string | null;
  profile_image_url: string;
};

export type CreateContentDraftRequest = {
  merchantId: string;
  targetCountry: string;
  platform: string;
  goal: string;
  inputBrief: string;
  websiteUrl: string;
  tone: string;
  mustInclude: string[];
  mustAvoid: string[];
  uploadedAssetIds: string[];
  applyImageVariant: boolean;
  imageVariantProvider: "none" | "nano_banana";
  publishMode: "draft";
};

export type InitAssetUploadRequest = {
  merchantId: string;
  filename: string;
  contentType: string;
  sizeBytes: number;
};

export type InitAssetUploadResponse = {
  assetId: string;
  uploadUrl: string;
  assetType: string;
};

export type CreateContentDraftResponse = {
  contentId: string;
  status: "draft" | "approved" | "scheduled" | "published" | "rejected";
  message: string;
};

export type ContentDetail = {
  content_id: string;
  merchant_id: string;
  target_country: string;
  platform: string;
  goal: string;
  status: "draft" | "approved" | "scheduled" | "published" | "rejected";
  title: string;
  body: string;
  hashtags: string[];
  must_include: string[];
  must_avoid: string[];
  uploaded_asset_ids: string[];
  apply_image_variant: boolean;
  image_variant_provider: "none" | "nano_banana";
  image_variant_job_id?: string | null;
  publish_job_id?: string | null;
  latest_publish_result_id?: string | null;
  publish_result_ids?: string[];
  approval_required: boolean;
  created_at: string;
  updated_at: string;
  variant_asset_ids?: string[];
};

export type ContentListItem = {
  content_id: string;
  merchant_id: string;
  target_country: string;
  platform: string;
  goal: string;
  status: "draft" | "approved" | "scheduled" | "published" | "rejected";
  apply_image_variant: boolean;
  image_variant_provider: "none" | "nano_banana";
  variant_asset_ids: string[];
  latest_publish_result_id?: string | null;
  created_at: string;
  updated_at: string;
};

export type ContentApproveRequest = {
  approverId: string;
  comment?: string;
};

export type ContentRejectRequest = {
  reviewerId: string;
  reason: string;
};

export type ContentPublishRequest = {
  publishAt?: string;
  applyImageVariant: boolean;
  imageVariantProvider: "none" | "nano_banana";
  sourceAssetIds: string[];
};

export type ContentPublishResponse = {
  content_id: string;
  status: "scheduled" | "published" | "draft" | "approved" | "rejected";
  job_id: string;
  publish_at?: string | null;
  image_variant_job_id?: string | null;
  image_variant_provider?: "none" | "nano_banana" | null;
  publish_result_id?: string | null;
};

export type ReviewDetail = {
  review_id: string;
  merchant_id: string;
  platform: string;
  rating: number;
  language: string;
  review_text: string;
  sensitivity: "low" | "medium" | "high";
  status: "draft" | "approved";
  reply_draft: string;
  escalated: boolean;
  created_at: string;
};

export type ReviewListItem = {
  review_id: string;
  merchant_id: string;
  platform: string;
  rating: number;
  language: string;
  sensitivity: "low" | "medium" | "high";
  status: "draft" | "approved";
  escalated: boolean;
  created_at: string;
};

export type ReviewApproveReplyRequest = {
  approverId: string;
  replyText?: string;
};

export type ReviewApproveReplyResponse = {
  review_id: string;
  status: "draft" | "approved";
  approved_reply_text: string;
};

export type JobStatusResponse = {
  job_id: string;
  job_type: string;
  status: "queued" | "running" | "succeeded" | "failed";
  resource_type: string;
  resource_id: string;
  created_at: string;
  updated_at: string;
};

export type JobListItem = JobStatusResponse;

export type MonthlyReportGenerateRequest = {
  scopeType: "merchant" | "program";
  scopeId: string;
  year: number;
  month: number;
};

export type MonthlyReportGenerateResponse = {
  report_id: string;
  job_id: string;
  status: string;
};

export type ReportListItem = {
  report_id: string;
  scope_type: string;
  scope_id: string;
  year: number;
  month: number;
  status: string;
  created_at: string;
};

export type AssetDetail = {
  asset_id: string;
  merchant_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  asset_type: string;
  status: string;
  provider?: string | null;
  generated_by_job_id?: string | null;
  source_asset_ids: string[];
  created_at: string;
  updated_at: string;
};

export type AssetListItem = AssetDetail;

export type PublishResultDetail = {
  publish_result_id: string;
  content_id: string;
  channel: string;
  adapter_name: string;
  status: string;
  external_post_id?: string | null;
  external_url?: string | null;
  publish_at?: string | null;
  source_asset_ids: string[];
  variant_asset_ids: string[];
  image_variant_provider?: "none" | "nano_banana" | null;
  thumbnail_url?: string | null;
  title?: string | null;
  caption_preview?: string | null;
  created_at: string;
  updated_at: string;
};

export type PublishResultListItem = {
  publish_result_id: string;
  content_id: string;
  channel: string;
  adapter_name: string;
  status: string;
  external_post_id?: string | null;
  external_url?: string | null;
  publish_at?: string | null;
  thumbnail_url?: string | null;
  title?: string | null;
  caption_preview?: string | null;
  created_at: string;
  updated_at: string;
};

export type AuditLogEntry = {
  audit_log_id: string;
  request_id?: string | null;
  actor_role?: string | null;
  actor_id?: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type ObservabilityRequestEntry = {
  request_id: string;
  method: string;
  path: string;
  status_code: number;
  duration_ms: number;
  actor_role?: string | null;
  actor_id?: string | null;
  merchant_id?: string | null;
  created_at: string;
};

export type ObservabilitySummary = {
  total_requests: number;
  status_counts: Record<string, number>;
  path_counts: Record<string, number>;
  recent_request_ids: string[];
};

export type MerchantSummary = {
  merchant_id: string;
  content_count: number;
  pending_content_count: number;
  approved_content_count: number;
  review_count: number;
  pending_review_count: number;
  asset_count: number;
  report_count: number;
  latest_activity_at?: string | null;
};

function resolveApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
}

function actorHeaders(role: "merchant" | "admin", merchantId?: string, userId?: string) {
  const session = readAuthSession();
  const resolvedRole = (session?.role ?? role) as "merchant" | "admin";
  const resolvedUserId = userId ?? session?.userId ?? (resolvedRole === "admin" ? "admin_frontend" : "u_frontend");
  const resolvedMerchantId =
    resolvedRole === "merchant" ? merchantId ?? session?.merchantId ?? undefined : undefined;
  return {
    "Content-Type": "application/json",
    "X-Test-Role": resolvedRole,
    "X-Test-User-Id": resolvedUserId,
    ...(resolvedMerchantId ? { "X-Test-Merchant-Id": resolvedMerchantId } : {}),
  };
}

export async function login(payload: LoginRequest): Promise<AuthSession> {
  const response = await fetch(`${resolveApiBaseUrl()}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(body?.message ?? "로그인에 실패했습니다.");
  }

  const body = (await response.json()) as AuthSessionResponse;
  return {
    userId: body.user_id,
    email: body.email,
    displayName: body.display_name,
    role: body.role,
    merchantId: body.merchant_id,
    merchantName: body.merchant_name,
    profileImageUrl: body.profile_image_url,
  };
}

export async function listTestAccounts(): Promise<{ items: TestAccount[] }> {
  return requestJson<{ items: TestAccount[] }>(
    `${resolveApiBaseUrl()}/auth/test-accounts`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    },
    "테스트 계정 목록을 불러오지 못했습니다.",
  );
}

export async function initAssetUpload(
  payload: InitAssetUploadRequest,
): Promise<InitAssetUploadResponse> {
  const response = await fetch(`${resolveApiBaseUrl()}/assets/upload-init`, {
    method: "POST",
    headers: actorHeaders("merchant", payload.merchantId),
    body: JSON.stringify({
      merchant_id: payload.merchantId,
      filename: payload.filename,
      content_type: payload.contentType,
      size_bytes: payload.sizeBytes,
    }),
    cache: "no-store",
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(body?.message ?? "이미지 자산 등록에 실패했습니다.");
  }

  const body = (await response.json()) as {
    asset_id: string;
    upload_url: string;
    asset_type: string;
  };

  return {
    assetId: body.asset_id,
    uploadUrl: body.upload_url,
    assetType: body.asset_type,
  };
}

export async function createContentDraft(
  payload: CreateContentDraftRequest,
): Promise<CreateContentDraftResponse> {
  const response = await fetch(`${resolveApiBaseUrl()}/contents/generate`, {
    method: "POST",
    headers: actorHeaders("merchant", payload.merchantId),
    body: JSON.stringify({
      merchant_id: payload.merchantId,
      target_country: payload.targetCountry,
      platform: payload.platform,
      goal: payload.goal,
      input_brief: payload.inputBrief,
      website_url: payload.websiteUrl || undefined,
      tone: payload.tone || undefined,
      must_include: payload.mustInclude,
      must_avoid: payload.mustAvoid,
      uploaded_asset_ids: payload.uploadedAssetIds,
      apply_image_variant: payload.applyImageVariant,
      image_variant_provider: payload.imageVariantProvider,
      publish_mode: payload.publishMode,
    }),
    cache: "no-store",
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { message?: string } | null;
    throw new Error(body?.message ?? "초안 생성 요청에 실패했습니다.");
  }

  const body = (await response.json()) as {
    content_id: string;
    status: CreateContentDraftResponse["status"];
    message: string;
  };

  return {
    contentId: body.content_id,
    status: body.status,
    message: body.message,
  };
}

async function readErrorMessage(response: Response, fallback: string) {
  const body = (await response.json().catch(() => null)) as { message?: string } | null;
  return body?.message ?? fallback;
}

async function requestJson<TResponse>(input: RequestInfo | URL, init: RequestInit, fallback: string): Promise<TResponse> {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, fallback));
  }
  return (await response.json()) as TResponse;
}

export async function fetchContentDetail(contentId: string, merchantId = "m_123"): Promise<ContentDetail> {
  return requestJson<ContentDetail>(
    `${resolveApiBaseUrl()}/contents/${contentId}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", merchantId),
      cache: "no-store",
    },
    "콘텐츠를 불러오지 못했습니다.",
  );
}

export async function listContents(params?: {
  merchantId?: string;
  status?: string;
  platform?: string;
}): Promise<{ items: ContentListItem[] }> {
  const search = new URLSearchParams();
  if (params?.merchantId) search.set("merchant_id", params.merchantId);
  if (params?.status) search.set("status", params.status);
  if (params?.platform) search.set("platform", params.platform);
  return requestJson<{ items: ContentListItem[] }>(
    `${resolveApiBaseUrl()}/contents${search.toString() ? `?${search.toString()}` : ""}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", params?.merchantId ?? "m_123"),
      cache: "no-store",
    },
    "콘텐츠 목록을 불러오지 못했습니다.",
  );
}

export async function approveContent(
  contentId: string,
  payload: ContentApproveRequest,
  merchantId = "m_123",
): Promise<{ content_id: string; status: string; approved_by?: string | null; approved_at?: string | null }> {
  return requestJson(
    `${resolveApiBaseUrl()}/contents/${contentId}/approve`,
    {
      method: "POST",
      headers: actorHeaders("merchant", merchantId, payload.approverId),
      body: JSON.stringify({
        approver_id: payload.approverId,
        comment: payload.comment || undefined,
      }),
      cache: "no-store",
    },
    "콘텐츠 승인을 완료하지 못했습니다.",
  );
}

export async function rejectContent(
  contentId: string,
  payload: ContentRejectRequest,
  merchantId = "m_123",
): Promise<{ content_id: string; status: string; rejected_by?: string | null; reason?: string | null }> {
  return requestJson(
    `${resolveApiBaseUrl()}/contents/${contentId}/reject`,
    {
      method: "POST",
      headers: actorHeaders("merchant", merchantId, payload.reviewerId),
      body: JSON.stringify({
        reviewer_id: payload.reviewerId,
        reason: payload.reason,
      }),
      cache: "no-store",
    },
    "콘텐츠 반려를 완료하지 못했습니다.",
  );
}

export async function publishContent(
  contentId: string,
  payload: ContentPublishRequest,
  merchantId = "m_123",
): Promise<ContentPublishResponse> {
  return requestJson<ContentPublishResponse>(
    `${resolveApiBaseUrl()}/contents/${contentId}/publish`,
    {
      method: "POST",
      headers: actorHeaders("merchant", merchantId),
      body: JSON.stringify({
        publish_at: payload.publishAt || undefined,
        apply_image_variant: payload.applyImageVariant,
        image_variant_provider: payload.imageVariantProvider,
        source_asset_ids: payload.sourceAssetIds,
      }),
      cache: "no-store",
    },
    "콘텐츠 발행 요청에 실패했습니다.",
  );
}

export async function fetchReviewDetail(reviewId: string, merchantId = "m_123"): Promise<ReviewDetail> {
  return requestJson<ReviewDetail>(
    `${resolveApiBaseUrl()}/reviews/${reviewId}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", merchantId),
      cache: "no-store",
    },
    "리뷰를 불러오지 못했습니다.",
  );
}

export async function listReviews(params?: {
  merchantId?: string;
  status?: string;
  sensitivity?: string;
}): Promise<{ items: ReviewListItem[] }> {
  const search = new URLSearchParams();
  if (params?.merchantId) search.set("merchant_id", params.merchantId);
  if (params?.status) search.set("status", params.status);
  if (params?.sensitivity) search.set("sensitivity", params.sensitivity);
  return requestJson<{ items: ReviewListItem[] }>(
    `${resolveApiBaseUrl()}/reviews${search.toString() ? `?${search.toString()}` : ""}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", params?.merchantId ?? "m_123"),
      cache: "no-store",
    },
    "리뷰 목록을 불러오지 못했습니다.",
  );
}

export async function approveReviewReply(
  reviewId: string,
  payload: ReviewApproveReplyRequest,
  merchantId = "m_123",
): Promise<ReviewApproveReplyResponse> {
  return requestJson<ReviewApproveReplyResponse>(
    `${resolveApiBaseUrl()}/reviews/${reviewId}/approve-reply`,
    {
      method: "POST",
      headers: actorHeaders("merchant", merchantId, payload.approverId),
      body: JSON.stringify({
        approver_id: payload.approverId,
        reply_text: payload.replyText || undefined,
      }),
      cache: "no-store",
    },
    "리뷰 답글 승인을 완료하지 못했습니다.",
  );
}

export async function fetchJobStatus(jobId: string, merchantId = "m_123"): Promise<JobStatusResponse> {
  return requestJson<JobStatusResponse>(
    `${resolveApiBaseUrl()}/jobs/${jobId}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", merchantId),
      cache: "no-store",
    },
    "작업 상태를 불러오지 못했습니다.",
  );
}

export async function listJobs(params?: {
  merchantId?: string;
  resourceType?: string;
  status?: string;
}): Promise<{ items: JobListItem[] }> {
  const search = new URLSearchParams();
  if (params?.resourceType) search.set("resource_type", params.resourceType);
  if (params?.status) search.set("status", params.status);
  return requestJson<{ items: JobListItem[] }>(
    `${resolveApiBaseUrl()}/jobs${search.toString() ? `?${search.toString()}` : ""}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", params?.merchantId ?? "m_123"),
      cache: "no-store",
    },
    "작업 목록을 불러오지 못했습니다.",
  );
}

export async function generateMonthlyReport(
  payload: MonthlyReportGenerateRequest,
): Promise<MonthlyReportGenerateResponse> {
  return requestJson<MonthlyReportGenerateResponse>(
    `${resolveApiBaseUrl()}/reports/monthly/generate`,
    {
      method: "POST",
      headers: actorHeaders("merchant", payload.scopeId),
      body: JSON.stringify({
        scope_type: payload.scopeType,
        scope_id: payload.scopeId,
        year: payload.year,
        month: payload.month,
      }),
      cache: "no-store",
    },
    "월간 리포트 생성을 요청하지 못했습니다.",
  );
}

export async function listReports(params?: {
  scopeType?: string;
  scopeId?: string;
  status?: string;
}): Promise<{ items: ReportListItem[] }> {
  const search = new URLSearchParams();
  if (params?.scopeType) search.set("scope_type", params.scopeType);
  if (params?.scopeId) search.set("scope_id", params.scopeId);
  if (params?.status) search.set("status", params.status);
  return requestJson<{ items: ReportListItem[] }>(
    `${resolveApiBaseUrl()}/reports${search.toString() ? `?${search.toString()}` : ""}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", params?.scopeId ?? "m_123"),
      cache: "no-store",
    },
    "리포트 목록을 불러오지 못했습니다.",
  );
}

export async function listAssets(params?: {
  merchantId?: string;
  assetType?: string;
  status?: string;
}): Promise<{ items: AssetListItem[] }> {
  const search = new URLSearchParams();
  if (params?.merchantId) search.set("merchant_id", params.merchantId);
  if (params?.assetType) search.set("asset_type", params.assetType);
  if (params?.status) search.set("status", params.status);
  return requestJson<{ items: AssetListItem[] }>(
    `${resolveApiBaseUrl()}/assets${search.toString() ? `?${search.toString()}` : ""}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", params?.merchantId ?? "m_123"),
      cache: "no-store",
    },
    "자산 목록을 불러오지 못했습니다.",
  );
}

export async function fetchAssetDetail(assetId: string, merchantId = "m_123"): Promise<AssetDetail> {
  return requestJson<AssetDetail>(
    `${resolveApiBaseUrl()}/assets/${assetId}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", merchantId),
      cache: "no-store",
    },
    "자산 상세를 불러오지 못했습니다.",
  );
}

export async function listPublishResults(merchantId = "m_123"): Promise<{ items: PublishResultListItem[] }> {
  return requestJson<{ items: PublishResultListItem[] }>(
    `${resolveApiBaseUrl()}/publish-results`,
    {
      method: "GET",
      headers: actorHeaders("merchant", merchantId),
      cache: "no-store",
    },
    "발행 결과 목록을 불러오지 못했습니다.",
  );
}

export async function fetchPublishResult(publishResultId: string, merchantId = "m_123"): Promise<PublishResultDetail> {
  return requestJson<PublishResultDetail>(
    `${resolveApiBaseUrl()}/publish-results/${publishResultId}`,
    {
      method: "GET",
      headers: actorHeaders("merchant", merchantId),
      cache: "no-store",
    },
    "발행 결과를 불러오지 못했습니다.",
  );
}

function adminHeaders() {
  return actorHeaders("admin");
}

export async function listMerchantSummaries(): Promise<{ items: MerchantSummary[] }> {
  return requestJson<{ items: MerchantSummary[] }>(
    `${resolveApiBaseUrl()}/admin/merchants`,
    {
      method: "GET",
      headers: adminHeaders(),
      cache: "no-store",
    },
    "점포 목록을 불러오지 못했습니다.",
  );
}

export async function listAuditLogs(params?: {
  action?: string;
  resourceType?: string;
  actorId?: string;
}): Promise<{ items: AuditLogEntry[] }> {
  const search = new URLSearchParams();
  if (params?.action) search.set("action", params.action);
  if (params?.resourceType) search.set("resource_type", params.resourceType);
  if (params?.actorId) search.set("actor_id", params.actorId);
  return requestJson<{ items: AuditLogEntry[] }>(
    `${resolveApiBaseUrl()}/audit-logs${search.toString() ? `?${search.toString()}` : ""}`,
    {
      method: "GET",
      headers: adminHeaders(),
      cache: "no-store",
    },
    "감사 로그를 불러오지 못했습니다.",
  );
}

export async function listObservabilityRequests(): Promise<{ items: ObservabilityRequestEntry[] }> {
  return requestJson<{ items: ObservabilityRequestEntry[] }>(
    `${resolveApiBaseUrl()}/observability/requests`,
    {
      method: "GET",
      headers: adminHeaders(),
      cache: "no-store",
    },
    "요청 추적 로그를 불러오지 못했습니다.",
  );
}

export async function fetchObservabilitySummary(): Promise<ObservabilitySummary> {
  return requestJson<ObservabilitySummary>(
    `${resolveApiBaseUrl()}/observability/summary`,
    {
      method: "GET",
      headers: adminHeaders(),
      cache: "no-store",
    },
    "관측 요약을 불러오지 못했습니다.",
  );
}
