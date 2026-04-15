"use client";

import Link from "next/link";
import { ChangeEvent, ReactNode, useEffect, useState } from "react";

import { readAuthSession } from "@/lib/auth";
import {
  approveContent,
  approveReviewReply,
  createContentDraft,
  fetchContentDetail,
  fetchReviewDetail,
  generateMonthlyReport,
  initAssetUpload,
  listContents,
  listJobs,
  listPublishResults,
  listReports,
  listReviews,
  publishContent,
  rejectContent,
} from "@/lib/api";

import styles from "./merchant-dashboard.module.css";

type ContentStatus = "draft" | "approved" | "scheduled" | "published" | "rejected";

type DraftRecord = {
  contentId: string;
  status: ContentStatus;
  message: string;
  platform: string;
  targetCountry: string;
  createdAt: string;
};

type RegisteredAsset = {
  assetId: string;
  filename: string;
  contentType: string;
  sizeBytes: number;
};

type ContentRequest = {
  merchantId: string;
  targetCountry: string;
  platform: string;
  goal: string;
  inputBrief: string;
  websiteUrl: string;
  tone: string;
  mustInclude: string;
  mustAvoid: string;
  applyImageVariant: boolean;
  imageVariantProvider: "none" | "nano_banana";
  publishMode: "draft";
};

const workflowSteps = [
  ["1", "대상과 채널 선택", "나라, 플랫폼, 목표를 정한다."],
  ["2", "메시지와 자산 입력", "brief와 업로드 이미지를 함께 등록한다."],
  ["3", "점주가 직접 승인 및 발행", "생성된 초안을 점주가 확인하고 바로 승인하거나 발행한다."],
] as const;

const initialForm: ContentRequest = {
  merchantId: "m_123",
  targetCountry: "JP",
  platform: "instagram",
  goal: "store_visit",
  inputBrief: "벚꽃 시즌에 맞춰 말차라떼와 푸딩을 강조하고 싶어요.",
  websiteUrl: "https://example.com",
  tone: "friendly",
  mustInclude: "말차라떼, 부산 여행",
  mustAvoid: "최고, 무조건",
  applyImageVariant: false,
  imageVariantProvider: "nano_banana",
  publishMode: "draft",
};

function splitTokens(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatBytes(sizeBytes: number) {
  if (sizeBytes < 1024 * 1024) {
    return `${Math.round(sizeBytes / 1024)} KB`;
  }

  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function MerchantDashboard() {
  const [mounted, setMounted] = useState(false);
  const [authSession, setAuthSession] = useState<ReturnType<typeof readAuthSession>>(null);
  const [form, setForm] = useState(initialForm);
  const [submitMessage, setSubmitMessage] = useState("draft 생성을 위한 입력을 준비하세요.");
  const [contentStatus, setContentStatus] = useState<ContentStatus>("draft");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [assets, setAssets] = useState<RegisteredAsset[]>([]);
  const [drafts, setDrafts] = useState<DraftRecord[]>([]);
  const [selectedContentId, setSelectedContentId] = useState("");
  const [contentDetail, setContentDetail] = useState<Awaited<ReturnType<typeof fetchContentDetail>> | null>(null);
  const [contentActionMessage, setContentActionMessage] = useState("생성된 콘텐츠를 선택하면 점주가 직접 승인과 발행을 처리할 수 있습니다.");
  const [pendingContents, setPendingContents] = useState<Awaited<ReturnType<typeof listContents>>["items"]>([]);
  const [selectedReviewId, setSelectedReviewId] = useState("");
  const [reviewQueue, setReviewQueue] = useState<Awaited<ReturnType<typeof listReviews>>["items"]>([]);
  const [reviewDetail, setReviewDetail] = useState<Awaited<ReturnType<typeof fetchReviewDetail>> | null>(null);
  const [reviewReplyText, setReviewReplyText] = useState("");
  const [reviewActionMessage, setReviewActionMessage] = useState("민감 리뷰도 점주 화면에서 직접 검토합니다.");
  const [jobs, setJobs] = useState<Awaited<ReturnType<typeof listJobs>>["items"]>([]);
  const [reports, setReports] = useState<Awaited<ReturnType<typeof listReports>>["items"]>([]);
  const [publishResults, setPublishResults] = useState<Awaited<ReturnType<typeof listPublishResults>>["items"]>([]);
  const [reportMessage, setReportMessage] = useState("월간 리포트를 생성하면 점주 기준 최근 작업이 누적됩니다.");
  const [isRefreshingOps, setIsRefreshingOps] = useState(false);

  const parsedMustInclude = splitTokens(form.mustInclude);
  const parsedMustAvoid = splitTokens(form.mustAvoid);
  const canSubmit = form.merchantId.trim().length > 0 && form.inputBrief.trim().length >= 10;
  const canEnableVariant = assets.length > 0;

  useEffect(() => {
    setMounted(true);
    const session = readAuthSession();
    setAuthSession(session);
    if (session?.merchantId) {
      setForm((current) => ({ ...current, merchantId: session.merchantId ?? current.merchantId }));
    }
  }, []);

  useEffect(() => {
    if (!mounted) {
      return;
    }
    async function bootstrap() {
      const latestContentId =
        typeof window !== "undefined" ? window.localStorage.getItem("harness.latestContentId") ?? "" : "";
      if (latestContentId) {
        setSelectedContentId(latestContentId);
        try {
          const detail = await fetchContentDetail(latestContentId, form.merchantId);
          setContentDetail(detail);
        } catch (error) {
          setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 상세를 불러오지 못했습니다.");
        }
      }
      setIsRefreshingOps(true);
      try {
        const [contents, reviews, jobItems, reportItems, publishItems] = await Promise.all([
          listContents({ merchantId: form.merchantId }),
          listReviews({ merchantId: form.merchantId }),
          listJobs({ merchantId: form.merchantId }),
          listReports({ scopeType: "merchant", scopeId: form.merchantId }),
          listPublishResults(form.merchantId),
        ]);
        setPendingContents(contents.items);
        setReviewQueue(reviews.items);
        setJobs(jobItems.items);
        setReports(reportItems.items);
        setPublishResults(publishItems.items);
      } catch (error) {
        setSubmitMessage(error instanceof Error ? error.message : "점주 작업 데이터를 불러오지 못했습니다.");
      } finally {
        setIsRefreshingOps(false);
      }
    }

    void bootstrap();
  }, [form.merchantId, mounted]);

  async function loadOperations() {
    setIsRefreshingOps(true);
    try {
      const [contents, reviews, jobItems, reportItems, publishItems] = await Promise.all([
        listContents({ merchantId: form.merchantId }),
        listReviews({ merchantId: form.merchantId }),
        listJobs({ merchantId: form.merchantId }),
        listReports({ scopeType: "merchant", scopeId: form.merchantId }),
        listPublishResults(form.merchantId),
      ]);
      setPendingContents(contents.items);
      setReviewQueue(reviews.items);
      setJobs(jobItems.items);
      setReports(reportItems.items);
      setPublishResults(publishItems.items);
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : "점주 작업 데이터를 불러오지 못했습니다.");
    } finally {
      setIsRefreshingOps(false);
    }
  }

  async function loadContentDetail(contentId: string) {
    try {
      const detail = await fetchContentDetail(contentId, form.merchantId);
      setContentDetail(detail);
      setSelectedContentId(contentId);
      if (typeof window !== "undefined") {
        window.localStorage.setItem("harness.latestContentId", contentId);
      }
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 상세를 불러오지 못했습니다.");
    }
  }

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    if (files.length === 0) {
      return;
    }

    setIsUploading(true);
    setSubmitMessage("업로드 자산을 등록하는 중입니다.");

    try {
      const uploaded = await Promise.all(
        files.map(async (file) => {
          const asset = await initAssetUpload({
            merchantId: form.merchantId,
            filename: file.name,
            contentType: file.type || "image/jpeg",
            sizeBytes: file.size,
          });

          return {
            assetId: asset.assetId,
            filename: file.name,
            contentType: file.type || "image/jpeg",
            sizeBytes: file.size,
          };
        }),
      );

      setAssets((current) => [...current, ...uploaded]);
      setSubmitMessage(`${uploaded.length}개 자산을 등록했습니다. draft 생성으로 진행할 수 있습니다.`);
      await loadOperations();
    } catch (error) {
      const message = error instanceof Error ? error.message : "이미지 자산 등록에 실패했습니다.";
      setSubmitMessage(message);
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  function removeAsset(assetId: string) {
    setAssets((current) => current.filter((asset) => asset.assetId !== assetId));
  }

  async function handleSubmit() {
    if (!canSubmit) {
      setSubmitMessage("강조 내용과 점포 정보를 먼저 확인해 주세요.");
      return;
    }
    if (form.applyImageVariant && !canEnableVariant) {
      setSubmitMessage("이미지 변형을 사용하려면 먼저 이미지를 등록해야 합니다.");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await createContentDraft({
        merchantId: form.merchantId,
        targetCountry: form.targetCountry,
        platform: form.platform,
        goal: form.goal,
        inputBrief: form.inputBrief,
        websiteUrl: form.websiteUrl,
        tone: form.tone,
        mustInclude: parsedMustInclude,
        mustAvoid: parsedMustAvoid,
        uploadedAssetIds: assets.map((asset) => asset.assetId),
        applyImageVariant: form.applyImageVariant,
        imageVariantProvider: form.applyImageVariant ? form.imageVariantProvider : "none",
        publishMode: form.publishMode,
      });

      const draftRecord: DraftRecord = {
        contentId: response.contentId,
        status: response.status,
        message: response.message,
        platform: form.platform,
        targetCountry: form.targetCountry,
        createdAt: new Date().toLocaleString("ko-KR"),
      };

      setContentStatus(response.status);
      setDrafts((current) => [draftRecord, ...current].slice(0, 5));
      setSelectedContentId(response.contentId);
      setSubmitMessage(response.message);
      await loadOperations();
      await loadContentDetail(response.contentId);
    } catch (error) {
      const message = error instanceof Error ? error.message : "초안 생성 요청에 실패했습니다.";
      setSubmitMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleApproveContent() {
    if (!contentDetail) {
      setContentActionMessage("먼저 콘텐츠를 선택해 주세요.");
      return;
    }

    try {
      await approveContent(
        contentDetail.content_id,
        {
          approverId: authSession?.userId ?? "merchant_owner",
          comment: "점주 확인 완료",
        },
        form.merchantId,
      );
      setContentActionMessage("점주 승인 완료");
      await loadOperations();
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 승인에 실패했습니다.");
    }
  }

  async function handleRejectContent() {
    if (!contentDetail) {
      setContentActionMessage("먼저 콘텐츠를 선택해 주세요.");
      return;
    }

    try {
      await rejectContent(
        contentDetail.content_id,
        {
          reviewerId: authSession?.userId ?? "merchant_owner",
          reason: "점주 검토 후 수정 필요",
        },
        form.merchantId,
      );
      setContentActionMessage("점주 반려 완료");
      await loadOperations();
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 반려에 실패했습니다.");
    }
  }

  async function handlePublishContent() {
    if (!contentDetail) {
      setContentActionMessage("먼저 콘텐츠를 선택해 주세요.");
      return;
    }

    try {
      const response = await publishContent(
        contentDetail.content_id,
        {
          applyImageVariant: contentDetail.apply_image_variant,
          imageVariantProvider: contentDetail.image_variant_provider,
          sourceAssetIds: contentDetail.uploaded_asset_ids,
        },
        form.merchantId,
      );
      setContentActionMessage(`발행 예약 완료: ${response.job_id}`);
      await loadOperations();
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 발행에 실패했습니다.");
    }
  }

  async function handleSelectReview(reviewId: string) {
    const selected = await fetchReviewDetail(reviewId, form.merchantId);
    setSelectedReviewId(reviewId);
    setReviewDetail(selected);
    setReviewReplyText(selected.reply_draft);
  }

  async function handleApproveReview() {
    if (!selectedReviewId) {
      setReviewActionMessage("먼저 리뷰를 선택해 주세요.");
      return;
    }

    try {
      const response = await approveReviewReply(
        selectedReviewId,
        {
          approverId: authSession?.userId ?? "merchant_owner",
          replyText: reviewReplyText || undefined,
        },
        form.merchantId,
      );
      setReviewActionMessage(`답글 승인 완료: ${response.review_id}`);
      await loadOperations();
    } catch (error) {
      setReviewActionMessage(error instanceof Error ? error.message : "리뷰 답글 승인에 실패했습니다.");
    }
  }

  async function handleGenerateReport() {
    try {
      const response = await generateMonthlyReport({
        scopeType: "merchant",
        scopeId: form.merchantId,
        year: 2026,
        month: 4,
      });
      setReportMessage(`월간 리포트 생성 요청 완료: ${response.report_id}`);
      await loadOperations();
    } catch (error) {
      setReportMessage(error instanceof Error ? error.message : "리포트 생성에 실패했습니다.");
    }
  }

  if (!mounted || !authSession || authSession.role !== "merchant") {
    return (
      <main className={styles.page}>
        <section className={styles.shell}>
          <article className={styles.panel}>
            <p className={styles.cardLabel}>Merchant Access</p>
            <h1 className={styles.panelTitle}>{mounted ? "점주 계정으로 로그인해야 합니다." : "점주 화면을 준비하는 중입니다."}</h1>
            <p className={styles.notice}>
              {mounted
                ? "`test2@email.com`, `test3@email.com`, `test4@email.com` 중 하나로 로그인한 뒤 다시 들어오세요."
                : "세션을 확인하고 있습니다."}
            </p>
            <div className={styles.actions}>
              <Link href="/" className={styles.secondaryLink}>
                홈으로 이동
              </Link>
            </div>
          </article>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.page}>
      <section className={styles.shell}>
        <header className={styles.hero}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>Merchant Workspace</p>
            <h1 className={styles.heroTitle}>점주용 운영 화면</h1>
            <p className={styles.heroDescription}>
              점주는 콘텐츠 생성부터 승인, 반려, 발행, 리뷰 답글 승인, 리포트 요청까지 모두 이 화면에서 처리한다.
            </p>
            <p className={styles.heroDescription}>
              현재 로그인: {authSession?.displayName ?? "미로그인"} {authSession?.merchantName ? `· ${authSession.merchantName}` : ""}
            </p>
          </div>
          <nav className={styles.heroActions}>
            <Link href="/" className={styles.secondaryLink}>
              홈
            </Link>
            <Link href="/admin" className={styles.secondaryLink}>
              관리자 화면
            </Link>
          </nav>
        </header>

        <section className={styles.layout}>
          <div className={styles.mainColumn}>
            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Workflow</p>
                  <h2 className={styles.panelTitle}>입력 {"->"} 점주 승인 {"->"} 점주 발행</h2>
                </div>
                <span className={styles.statusBadge}>{contentStatus}</span>
              </div>

              <div className={styles.workflowGrid}>
                {workflowSteps.map(([step, title, detail]) => (
                  <div key={title} className={styles.workflowCard}>
                    <span className={styles.stepToken}>{step}</span>
                    <strong className={styles.workflowTitle}>{title}</strong>
                    <p className={styles.cardDescription}>{detail}</p>
                  </div>
                ))}
              </div>
            </article>

            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Content Request</p>
                  <h2 className={styles.panelTitle}>점주 입력 폼</h2>
                </div>
                <span className={styles.helperBadge}>{isUploading ? "uploading" : "ready"}</span>
              </div>

              <div className={styles.formGrid}>
                <Field label="대상 국가">
                  <select
                    value={form.targetCountry}
                    onChange={(event) => setForm({ ...form, targetCountry: event.target.value })}
                    className={styles.input}
                  >
                    <option value="JP">일본</option>
                    <option value="US">미국</option>
                    <option value="CN">중국</option>
                    <option value="TW">대만</option>
                    <option value="HK">홍콩</option>
                  </select>
                </Field>

                <Field label="플랫폼">
                  <select
                    value={form.platform}
                    onChange={(event) => setForm({ ...form, platform: event.target.value })}
                    className={styles.input}
                  >
                    <option value="instagram">Instagram</option>
                    <option value="google_business">Google Business</option>
                    <option value="blog">Blog</option>
                    <option value="xiaohongshu">Xiaohongshu</option>
                  </select>
                </Field>

                <Field label="목표">
                  <select
                    value={form.goal}
                    onChange={(event) => setForm({ ...form, goal: event.target.value })}
                    className={styles.input}
                  >
                    <option value="store_visit">매장 방문 유도</option>
                    <option value="awareness">인지도 확산</option>
                    <option value="seasonal_promotion">시즌 프로모션</option>
                    <option value="review_response">리뷰 유입 보조</option>
                  </select>
                </Field>

                <Field label="톤">
                  <select
                    value={form.tone}
                    onChange={(event) => setForm({ ...form, tone: event.target.value })}
                    className={styles.input}
                  >
                    <option value="friendly">친근한 느낌</option>
                    <option value="professional">신뢰감 있는 느낌</option>
                    <option value="trendy">감각적인 느낌</option>
                    <option value="calm">차분한 느낌</option>
                  </select>
                </Field>

                <Field label="홈페이지 URL" wide>
                  <input
                    value={form.websiteUrl}
                    onChange={(event) => setForm({ ...form, websiteUrl: event.target.value })}
                    className={styles.input}
                    placeholder="https://example.com"
                  />
                </Field>

                <Field label="강조 내용" wide>
                  <textarea
                    value={form.inputBrief}
                    onChange={(event) => setForm({ ...form, inputBrief: event.target.value })}
                    className={styles.textarea}
                    rows={4}
                  />
                </Field>

                <Field label="꼭 포함할 표현">
                  <input
                    value={form.mustInclude}
                    onChange={(event) => setForm({ ...form, mustInclude: event.target.value })}
                    className={styles.input}
                  />
                </Field>

                <Field label="피해야 할 표현">
                  <input
                    value={form.mustAvoid}
                    onChange={(event) => setForm({ ...form, mustAvoid: event.target.value })}
                    className={styles.input}
                  />
                </Field>

                <Field label="이미지 업로드" wide hint="현재 단계에서는 파일 메타데이터를 upload-init으로 등록합니다.">
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    multiple
                    onChange={handleFileChange}
                    className={styles.fileInput}
                  />
                </Field>
              </div>

              <div className={styles.assetPanel}>
                <div className={styles.assetHeader}>
                  <div>
                    <p className={styles.cardLabel}>Registered Assets</p>
                    <h3 className={styles.assetTitle}>현재 등록된 이미지 자산</h3>
                  </div>
                  <span className={styles.assetCount}>{assets.length}건</span>
                </div>

                {assets.length > 0 ? (
                  <div className={styles.assetList}>
                    {assets.map((asset) => (
                      <div key={asset.assetId} className={styles.assetCard}>
                        <div>
                          <strong className={styles.assetName}>{asset.filename}</strong>
                          <p className={styles.assetMeta}>
                            {asset.assetId} · {asset.contentType} · {formatBytes(asset.sizeBytes)}
                          </p>
                        </div>
                        <button type="button" onClick={() => removeAsset(asset.assetId)} className={styles.ghostButton}>
                          제거
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className={styles.emptyState}>등록된 이미지가 없습니다.</p>
                )}

                <label className={styles.variantToggle}>
                  <input
                    type="checkbox"
                    checked={form.applyImageVariant}
                    disabled={!canEnableVariant}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        applyImageVariant: event.target.checked,
                        imageVariantProvider: event.target.checked ? "nano_banana" : "none",
                      })
                    }
                  />
                  <div>
                    <strong>발행 시 이미지 변형 사용</strong>
                    <p className={styles.variantDescription}>
                      등록된 원본 자산을 기준으로 variant 이미지를 추가 생성한다.
                    </p>
                  </div>
                </label>
              </div>

              <div className={styles.notice}>{submitMessage}</div>
              <div className={styles.actions}>
                <button type="button" onClick={handleSubmit} className={styles.primaryButton} disabled={!canSubmit || isSubmitting}>
                  {isSubmitting ? "생성 중..." : "draft 생성"}
                </button>
                <button type="button" onClick={() => void loadOperations()} className={styles.ghostButton} disabled={isRefreshingOps}>
                  {isRefreshingOps ? "새로고침 중..." : "운영 데이터 새로고침"}
                </button>
              </div>
            </article>

            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Merchant Actions</p>
                  <h2 className={styles.panelTitle}>점주 승인 및 발행</h2>
                </div>
              </div>
              <div className={styles.queueList}>
                {pendingContents.length > 0 ? (
                  pendingContents.map((item) => (
                    <button
                      key={item.content_id}
                      type="button"
                      className={styles.queueCard}
                      onClick={() => void loadContentDetail(item.content_id)}
                    >
                      <strong>{item.content_id}</strong>
                      <span>{item.platform}</span>
                      <span>{item.status}</span>
                    </button>
                  ))
                ) : (
                  <p className={styles.emptyState}>생성된 콘텐츠가 아직 없습니다.</p>
                )}
              </div>
              {contentDetail ? (
                <div className={styles.operationPanel}>
                  <div className={styles.summaryGrid}>
                    <span>상태: {contentDetail.status}</span>
                    <span>플랫폼: {contentDetail.platform}</span>
                    <span>국가: {contentDetail.target_country}</span>
                    <span>자산 수: {contentDetail.uploaded_asset_ids.length}</span>
                  </div>
                  <p className={styles.assetTitle}>{contentDetail.title}</p>
                  <p className={styles.cardDescription}>{contentDetail.body}</p>
                  <p className={styles.assetMeta}>hashtags: {contentDetail.hashtags.join(" ")}</p>
                  <div className={styles.actions}>
                    <button type="button" onClick={handleApproveContent} className={styles.ghostButton}>
                      점주 승인
                    </button>
                    <button type="button" onClick={handleRejectContent} className={styles.ghostButton}>
                      점주 반려
                    </button>
                    <button type="button" onClick={handlePublishContent} className={styles.primaryButton}>
                      점주 발행
                    </button>
                  </div>
                </div>
              ) : null}
              <div className={styles.notice}>{contentActionMessage}</div>
            </article>

            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Review Actions</p>
                  <h2 className={styles.panelTitle}>리뷰 답글 승인</h2>
                </div>
              </div>
              <div className={styles.queueList}>
                {reviewQueue.length > 0 ? (
                  reviewQueue.map((item) => (
                    <button
                      key={item.review_id}
                      type="button"
                      className={styles.queueCard}
                      onClick={() => void handleSelectReview(item.review_id)}
                    >
                      <strong>{item.review_id}</strong>
                      <span>{item.sensitivity}</span>
                      <span>{item.status}</span>
                    </button>
                  ))
                ) : (
                  <p className={styles.emptyState}>점주가 검토할 리뷰가 없습니다.</p>
                )}
              </div>
              {reviewDetail ? (
                <div className={styles.operationPanel}>
                  <p className={styles.assetTitle}>{reviewDetail.review_id}</p>
                  <p className={styles.assetMeta}>
                    {reviewDetail.platform} · 평점 {reviewDetail.rating} · {reviewDetail.language}
                  </p>
                  <p className={styles.cardDescription}>{reviewDetail.review_text}</p>
                  <textarea
                    value={reviewReplyText}
                    onChange={(event) => setReviewReplyText(event.target.value)}
                    className={styles.textarea}
                    rows={4}
                    placeholder="답글 초안을 입력하거나 수정하세요."
                  />
                  <div className={styles.actions}>
                    <button type="button" onClick={handleApproveReview} className={styles.primaryButton}>
                      점주 답글 승인
                    </button>
                  </div>
                </div>
              ) : null}
              <div className={styles.notice}>{reviewActionMessage}</div>
            </article>
          </div>

          <aside className={styles.sideColumn}>
            <article className={styles.panel}>
              <p className={styles.cardLabel}>Input Summary</p>
              <div className={styles.summaryGrid}>
                <span>국가: {form.targetCountry}</span>
                <span>플랫폼: {form.platform}</span>
                <span>목표: {form.goal}</span>
                <span>자산 수: {assets.length}</span>
                <span>포함 표현: {parsedMustInclude.join(", ") || "-"}</span>
                <span>회피 표현: {parsedMustAvoid.join(", ") || "-"}</span>
                <span>이미지 변형: {form.applyImageVariant ? form.imageVariantProvider : "사용 안 함"}</span>
                <span>선택 콘텐츠: {selectedContentId || "-"}</span>
                <span>계정: {authSession?.email ?? "-"}</span>
              </div>
            </article>

            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Recent Drafts</p>
                  <h2 className={styles.panelTitle}>최근 생성 결과</h2>
                </div>
              </div>

              <div className={styles.draftList}>
                {drafts.length > 0 ? (
                  drafts.map((draft) => (
                    <div key={draft.contentId} className={styles.draftCard}>
                      <div className={styles.draftRow}>
                        <span className={styles.helperBadge}>{draft.status}</span>
                        <span className={styles.draftTime}>{draft.createdAt}</span>
                      </div>
                      <strong className={styles.draftTitle}>
                        {draft.targetCountry} / {draft.platform}
                      </strong>
                      <p className={styles.cardDescription}>{draft.message}</p>
                      <p className={styles.assetMeta}>{draft.contentId}</p>
                    </div>
                  ))
                ) : (
                  <p className={styles.emptyState}>아직 생성된 draft가 없습니다.</p>
                )}
              </div>
            </article>

            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Operations</p>
                  <h2 className={styles.panelTitle}>점주 작업 현황</h2>
                </div>
              </div>
              <div className={styles.summaryGrid}>
                <span>작업 수: {jobs.length}</span>
                <span>리포트 수: {reports.length}</span>
                <span>발행 결과: {publishResults.length}</span>
                <span>대기 콘텐츠: {pendingContents.filter((item) => item.status === "draft").length}</span>
              </div>
              <div className={styles.actions}>
                <button type="button" onClick={handleGenerateReport} className={styles.primaryButton}>
                  월간 리포트 생성
                </button>
              </div>
              <div className={styles.notice}>{reportMessage}</div>
            </article>

            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Published Examples</p>
                  <h2 className={styles.panelTitle}>게시 예시와 썸네일</h2>
                </div>
              </div>
              <div className={styles.draftList}>
                {publishResults.length > 0 ? (
                  publishResults.map((item) => (
                    <a key={item.publish_result_id} href={item.external_url ?? "#"} className={styles.exampleCard} target="_blank" rel="noreferrer">
                      {item.thumbnail_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={item.thumbnail_url} alt={item.title ?? item.publish_result_id} className={styles.exampleImage} />
                      ) : null}
                      <div className={styles.exampleBody}>
                        <strong className={styles.draftTitle}>{item.title ?? item.publish_result_id}</strong>
                        <p className={styles.cardDescription}>{item.caption_preview ?? item.channel}</p>
                        <p className={styles.assetMeta}>{item.external_url ?? item.publish_result_id}</p>
                      </div>
                    </a>
                  ))
                ) : (
                  <p className={styles.emptyState}>아직 게시 예시가 없습니다.</p>
                )}
              </div>
            </article>
          </aside>
        </section>
      </section>
    </main>
  );
}

function Field({
  label,
  wide = false,
  hint,
  children,
}: {
  label: string;
  wide?: boolean;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className={`${styles.field} ${wide ? styles.fieldWide : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      {children}
      {hint ? <span className={styles.fieldHint}>{hint}</span> : null}
    </label>
  );
}
