"use client";

import Link from "next/link";
import { ChangeEvent, ReactNode, useCallback, useEffect, useMemo, useState } from "react";

import { readAuthSession } from "@/lib/auth";
import {
  approveContent,
  approveReviewReply,
  createContentDraft,
  deleteContent,
  fetchAssetBinary,
  fetchAssetDetail,
  fetchContentDetail,
  fetchMerchantNanoBananaSetting,
  fetchReviewDetail,
  generateMonthlyReport,
  initAssetUpload,
  listContents,
  listJobs,
  listPublishResults,
  listReports,
  listReviews,
  publishContent,
  regenerateContentImage,
  rejectContent,
  saveMerchantNanoBananaSetting,
  updateContentOverlay,
  uploadAssetBinary,
} from "@/lib/api";

import styles from "./merchant-dashboard.module.css";

export type MerchantDashboardSection = "compose" | "content" | "overlay" | "reviews" | "ops";

type ContentStatus = "draft" | "approved" | "scheduled" | "published" | "rejected" | "deleted";

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
  status: string;
  localPreviewUrl?: string | null;
};

type ContentPreviewAsset = Awaited<ReturnType<typeof fetchAssetDetail>> & {
  objectUrl?: string | null;
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

const initialForm: ContentRequest = {
  merchantId: "m_123",
  targetCountry: "JP",
  platform: "instagram",
  goal: "store_visit",
  inputBrief: "벚꽃 시즌에 맞춰 매장 분위기와 대표 메뉴가 잘 보이는 카드형 게시물을 만들고 싶습니다.",
  websiteUrl: "https://example.com",
  tone: "friendly",
  mustInclude: "대표 메뉴, 시즌 한정",
  mustAvoid: "과장 표현, 허위 문구",
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

function revokePreviewAssets(items: ContentPreviewAsset[]) {
  items.forEach((asset) => {
    if (asset.objectUrl) {
      URL.revokeObjectURL(asset.objectUrl);
    }
  });
}

export function MerchantDashboard({ section }: { section: MerchantDashboardSection }) {
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
  const [contentAssets, setContentAssets] = useState<ContentPreviewAsset[]>([]);
  const [variantAssets, setVariantAssets] = useState<ContentPreviewAsset[]>([]);
  const [selectedVariantAssetId, setSelectedVariantAssetId] = useState("");
  const [contentActionMessage, setContentActionMessage] = useState("콘텐츠를 선택하면 점주가 직접 운영 액션을 처리할 수 있습니다.");
  const [pendingContents, setPendingContents] = useState<Awaited<ReturnType<typeof listContents>>["items"]>([]);
  const [selectedReviewId, setSelectedReviewId] = useState("");
  const [reviewQueue, setReviewQueue] = useState<Awaited<ReturnType<typeof listReviews>>["items"]>([]);
  const [reviewDetail, setReviewDetail] = useState<Awaited<ReturnType<typeof fetchReviewDetail>> | null>(null);
  const [reviewReplyText, setReviewReplyText] = useState("");
  const [reviewActionMessage, setReviewActionMessage] = useState("리뷰 답글 검토 화면입니다.");
  const [jobs, setJobs] = useState<Awaited<ReturnType<typeof listJobs>>["items"]>([]);
  const [reports, setReports] = useState<Awaited<ReturnType<typeof listReports>>["items"]>([]);
  const [publishResults, setPublishResults] = useState<Awaited<ReturnType<typeof listPublishResults>>["items"]>([]);
  const [reportMessage, setReportMessage] = useState("월간 리포트 생성 요청도 여기서 바로 보낼 수 있습니다.");
  const [isRefreshingOps, setIsRefreshingOps] = useState(false);
  const [nanoBananaApiKey, setNanoBananaApiKey] = useState("");
  const [nanoBananaMaskedKey, setNanoBananaMaskedKey] = useState<string | null>(null);
  const [nanoBananaMessage, setNanoBananaMessage] = useState("Nano Banana API 키를 저장하면 draft 생성과 동시에 1차 이미지 생성이 시작됩니다.");
  const [isLoadingNanoBanana, setIsLoadingNanoBanana] = useState(false);
  const [isSavingNanoBanana, setIsSavingNanoBanana] = useState(false);
  const [isRegeneratingImage, setIsRegeneratingImage] = useState(false);
  const [overlayHeadline, setOverlayHeadline] = useState("");
  const [overlaySubheadline, setOverlaySubheadline] = useState("");
  const [overlayCta, setOverlayCta] = useState("");
  const [overlayMessage, setOverlayMessage] = useState("생성 이미지 위에 올릴 텍스트를 따로 편집할 수 있습니다.");
  const [isSavingOverlay, setIsSavingOverlay] = useState(false);

  const parsedMustInclude = useMemo(() => splitTokens(form.mustInclude), [form.mustInclude]);
  const parsedMustAvoid = useMemo(() => splitTokens(form.mustAvoid), [form.mustAvoid]);
  const canSubmit = form.merchantId.trim().length > 0 && form.inputBrief.trim().length >= 10;
  const canEnableVariant = assets.length > 0 && Boolean(nanoBananaMaskedKey);

  useEffect(() => {
    setMounted(true);
    const session = readAuthSession();
    setAuthSession(session);
    if (session?.merchantId) {
      setForm((current) => ({ ...current, merchantId: session.merchantId ?? current.merchantId }));
    }
  }, []);

  useEffect(() => {
    return () => {
      revokePreviewAssets(contentAssets);
      revokePreviewAssets(variantAssets);
    };
  }, [contentAssets, variantAssets]);

  const buildPreviewAssets = useCallback(async (assetIds: string[]) => {
    return Promise.all(
      assetIds.map(async (assetId) => {
        const asset = await fetchAssetDetail(assetId, form.merchantId);
        let objectUrl: string | null = null;
        try {
          const binary = await fetchAssetBinary(assetId, form.merchantId);
          objectUrl = URL.createObjectURL(binary);
        } catch {
          objectUrl = null;
        }
        return { ...asset, objectUrl };
      }),
    );
  }, [form.merchantId]);

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
      setSubmitMessage(error instanceof Error ? error.message : "운영 데이터를 새로고침하지 못했습니다.");
    } finally {
      setIsRefreshingOps(false);
    }
  }

  const loadContentDetail = useCallback(async (contentId: string) => {
    try {
      const detail = await fetchContentDetail(contentId, form.merchantId);
      const [sourceAssets, generatedAssets] = await Promise.all([
        buildPreviewAssets(detail.uploaded_asset_ids),
        buildPreviewAssets(detail.variant_asset_ids ?? []),
      ]);

      setContentAssets((current) => {
        revokePreviewAssets(current);
        return sourceAssets;
      });
      setVariantAssets((current) => {
        revokePreviewAssets(current);
        return generatedAssets;
      });
      setSelectedVariantAssetId(detail.selected_variant_asset_id ?? generatedAssets[0]?.asset_id ?? "");
      setOverlayHeadline(detail.overlay_headline ?? "");
      setOverlaySubheadline(detail.overlay_subheadline ?? "");
      setOverlayCta(detail.overlay_cta ?? "");
      setContentDetail(detail);
      setSelectedContentId(contentId);
      if (typeof window !== "undefined") {
        window.localStorage.setItem("harness.latestContentId", contentId);
      }
    } catch (error) {
      setContentAssets([]);
      setVariantAssets([]);
      setSelectedVariantAssetId("");
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 상세를 불러오지 못했습니다.");
    }
  }, [buildPreviewAssets, form.merchantId]);

  useEffect(() => {
    if (!mounted || !form.merchantId) {
      return;
    }

    async function bootstrap() {
      const latestContentId =
        typeof window !== "undefined" ? window.localStorage.getItem("harness.latestContentId") ?? "" : "";

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

        if (latestContentId) {
          await loadContentDetail(latestContentId);
        }
      } catch (error) {
        setSubmitMessage(error instanceof Error ? error.message : "운영 데이터를 불러오지 못했습니다.");
      } finally {
        setIsRefreshingOps(false);
      }
    }

    async function loadNanoBananaSetting() {
      setIsLoadingNanoBanana(true);
      try {
        const setting = await fetchMerchantNanoBananaSetting(form.merchantId);
        setNanoBananaMaskedKey(setting.masked_api_key ?? null);
        setNanoBananaMessage(
          setting.has_api_key
            ? `저장된 키: ${setting.masked_api_key ?? "마스킹 처리됨"}`
            : "아직 저장된 Nano Banana API 키가 없습니다.",
        );
      } catch (error) {
        setNanoBananaMessage(error instanceof Error ? error.message : "Nano Banana API 설정을 불러오지 못했습니다.");
      } finally {
        setIsLoadingNanoBanana(false);
      }
    }

    void bootstrap();
    void loadNanoBananaSetting();
  }, [form.merchantId, loadContentDetail, mounted]);

  async function handleSaveNanoBananaSetting() {
    if (!nanoBananaApiKey.trim()) {
      setNanoBananaMessage("저장할 Nano Banana API 키를 입력하세요.");
      return;
    }
    setIsSavingNanoBanana(true);
    try {
      const saved = await saveMerchantNanoBananaSetting(form.merchantId, nanoBananaApiKey.trim());
      setNanoBananaMaskedKey(saved.masked_api_key ?? null);
      setNanoBananaApiKey("");
      setNanoBananaMessage(`저장 완료: ${saved.masked_api_key ?? "마스킹 처리됨"}`);
    } catch (error) {
      setNanoBananaMessage(error instanceof Error ? error.message : "Nano Banana API 설정을 저장하지 못했습니다.");
    } finally {
      setIsSavingNanoBanana(false);
    }
  }

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    if (files.length === 0) {
      return;
    }
    setIsUploading(true);
    setSubmitMessage("이미지 자산을 업로드하는 중입니다.");
    try {
      const uploaded = await Promise.all(
        files.map(async (file) => {
          const asset = await initAssetUpload({
            merchantId: form.merchantId,
            filename: file.name,
            contentType: file.type || "image/jpeg",
            sizeBytes: file.size,
          });
          const upload = await uploadAssetBinary(asset.assetId, file, form.merchantId);
          return {
            assetId: asset.assetId,
            filename: file.name,
            contentType: file.type || "image/jpeg",
            sizeBytes: file.size,
            status: upload.status,
            localPreviewUrl: file.type.startsWith("image/") ? URL.createObjectURL(file) : null,
          };
        }),
      );
      setAssets((current) => [...current, ...uploaded]);
      setSubmitMessage(`${uploaded.length}개 자산 업로드를 완료했습니다.`);
      await loadOperations();
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : "이미지 자산 등록에 실패했습니다.");
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  function removeAsset(assetId: string) {
    setAssets((current) => {
      const target = current.find((asset) => asset.assetId === assetId);
      if (target?.localPreviewUrl) {
        URL.revokeObjectURL(target.localPreviewUrl);
      }
      return current.filter((asset) => asset.assetId !== assetId);
    });
  }

  async function handleSubmit() {
    if (!canSubmit) {
      setSubmitMessage("브리프와 점포 정보를 먼저 확인하세요.");
      return;
    }
    if (form.applyImageVariant && !nanoBananaMaskedKey) {
      setSubmitMessage("이미지 생성을 사용하려면 먼저 Nano Banana API 키를 저장하세요.");
      return;
    }
    if (form.applyImageVariant && assets.length === 0) {
      setSubmitMessage("이미지 생성을 사용하려면 먼저 원본 이미지를 업로드하세요.");
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
      setDrafts((current) => [draftRecord, ...current].slice(0, 5));
      setContentStatus(response.status);
      setSelectedContentId(response.contentId);
      setSubmitMessage(response.message);
      await loadOperations();
      await loadContentDetail(response.contentId);
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : "draft 생성에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleApproveContent() {
    if (!contentDetail) return;
    try {
      await approveContent(contentDetail.content_id, { approverId: authSession?.userId ?? "merchant_owner", comment: "ok" }, form.merchantId);
      setContentActionMessage("콘텐츠 승인 완료");
      await loadOperations();
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 승인 실패");
    }
  }

  async function handleRejectContent() {
    if (!contentDetail) return;
    try {
      await rejectContent(contentDetail.content_id, { reviewerId: authSession?.userId ?? "merchant_owner", reason: "수정 필요" }, form.merchantId);
      setContentActionMessage("콘텐츠 반려 완료");
      await loadOperations();
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 반려 실패");
    }
  }

  async function handlePublishContent() {
    if (!contentDetail) return;
    try {
      const response = await publishContent(
        contentDetail.content_id,
        {
          applyImageVariant: contentDetail.apply_image_variant,
          imageVariantProvider: contentDetail.image_variant_provider,
          sourceAssetIds: contentDetail.uploaded_asset_ids,
          selectedVariantAssetId,
        },
        form.merchantId,
      );
      setContentActionMessage(`발행 요청 완료: ${response.job_id}`);
      await loadOperations();
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 발행 실패");
    }
  }

  async function handleDeleteContent(contentId?: string) {
    const targetContentId = contentId ?? contentDetail?.content_id;
    if (!targetContentId) return;
    try {
      const response = await deleteContent(targetContentId, form.merchantId);
      setContentActionMessage(response.message);
      await loadOperations();
      if (selectedContentId === targetContentId) {
        setContentDetail(null);
        setContentAssets([]);
        setVariantAssets([]);
        setSelectedVariantAssetId("");
      }
    } catch (error) {
      setContentActionMessage(error instanceof Error ? error.message : "콘텐츠 삭제 실패");
    }
  }

  async function handleRegenerateImage() {
    if (!contentDetail) return;
    setIsRegeneratingImage(true);
    try {
      const response = await regenerateContentImage(contentDetail.content_id, contentDetail.uploaded_asset_ids, form.merchantId);
      setSelectedVariantAssetId(response.selected_variant_asset_id ?? response.variant_asset_ids[0] ?? "");
      setOverlayMessage("이미지를 다시 생성했습니다. 마음에 드는 후보를 선택하세요.");
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setOverlayMessage(error instanceof Error ? error.message : "이미지 재생성 실패");
    } finally {
      setIsRegeneratingImage(false);
    }
  }

  async function handleSaveOverlay() {
    if (!contentDetail) return;
    setIsSavingOverlay(true);
    try {
      const response = await updateContentOverlay(
        contentDetail.content_id,
        {
          selectedVariantAssetId,
          overlayHeadline,
          overlaySubheadline,
          overlayCta,
        },
        form.merchantId,
      );
      setSelectedVariantAssetId(response.selected_variant_asset_id ?? "");
      setOverlayMessage("오버레이 텍스트 저장 완료");
      await loadContentDetail(contentDetail.content_id);
    } catch (error) {
      setOverlayMessage(error instanceof Error ? error.message : "오버레이 저장 실패");
    } finally {
      setIsSavingOverlay(false);
    }
  }

  async function handleSelectReview(reviewId: string) {
    try {
      const selected = await fetchReviewDetail(reviewId, form.merchantId);
      setSelectedReviewId(reviewId);
      setReviewDetail(selected);
      setReviewReplyText(selected.reply_draft);
    } catch (error) {
      setReviewActionMessage(error instanceof Error ? error.message : "리뷰 조회 실패");
    }
  }

  async function handleApproveReview() {
    if (!selectedReviewId) return;
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
      setReviewActionMessage(error instanceof Error ? error.message : "답글 승인 실패");
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
      setReportMessage(error instanceof Error ? error.message : "리포트 생성 실패");
    }
  }

  if (!mounted || !authSession || authSession.role !== "merchant") {
    return (
      <main className={styles.page}>
        <section className={styles.shell}>
          <article className={styles.panel}>
            <p className={styles.cardLabel}>Merchant Access</p>
            <h1 className={styles.panelTitle}>점주 계정으로 로그인해야 합니다.</h1>
            <p className={styles.notice}>`test2@email.com`, `test3@email.com`, `test4@email.com` 중 하나로 로그인한 뒤 다시 들어오세요.</p>
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

  const selectedVariantAsset = variantAssets.find((asset) => asset.asset_id === selectedVariantAssetId) ?? variantAssets[0] ?? null;

  return (
    <main className={styles.page}>
      <section className={styles.shell}>
        <header className={styles.hero}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>Merchant Workspace</p>
            <h1 className={styles.heroTitle}>{titleForSection(section)}</h1>
            <p className={styles.heroDescription}>
              draft 생성 시점에 1차 이미지를 만들고, 이후 오버레이 텍스트는 별도 편집 화면에서 관리합니다.
            </p>
            <p className={styles.heroDescription}>현재 로그인: {authSession.displayName} / {authSession.email}</p>
          </div>
          <div className={styles.heroActions}>
            <span className={styles.helperBadge}>merchant</span>
            <span className={styles.statusBadge}>{contentStatus}</span>
          </div>
        </header>

        {section === "compose" ? (
          <>
            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Draft Builder</p>
                  <h2 className={styles.panelTitle}>원본 업로드와 1차 이미지 생성</h2>
                </div>
              </div>
              <div className={styles.formGrid}>
                <Field label="대상 국가">
                  <select value={form.targetCountry} onChange={(event) => setForm({ ...form, targetCountry: event.target.value })} className={styles.input}>
                    <option value="JP">일본</option>
                    <option value="US">미국</option>
                    <option value="CN">중국</option>
                    <option value="TW">대만</option>
                    <option value="HK">홍콩</option>
                  </select>
                </Field>
                <Field label="플랫폼">
                  <select value={form.platform} onChange={(event) => setForm({ ...form, platform: event.target.value })} className={styles.input}>
                    <option value="instagram">Instagram</option>
                    <option value="google_business">Google Business</option>
                    <option value="blog">Blog</option>
                    <option value="xiaohongshu">Xiaohongshu</option>
                  </select>
                </Field>
                <Field label="목표">
                  <select value={form.goal} onChange={(event) => setForm({ ...form, goal: event.target.value })} className={styles.input}>
                    <option value="store_visit">매장 방문</option>
                    <option value="awareness">인지도</option>
                    <option value="seasonal_promotion">시즌 프로모션</option>
                    <option value="review_response">리뷰 대응</option>
                  </select>
                </Field>
                <Field label="톤">
                  <select value={form.tone} onChange={(event) => setForm({ ...form, tone: event.target.value })} className={styles.input}>
                    <option value="friendly">친근함</option>
                    <option value="professional">전문적</option>
                    <option value="trendy">트렌디</option>
                    <option value="calm">차분함</option>
                  </select>
                </Field>
                <Field label="웹사이트 URL" wide>
                  <input value={form.websiteUrl} onChange={(event) => setForm({ ...form, websiteUrl: event.target.value })} className={styles.input} />
                </Field>
                <Field label="브리프" wide>
                  <textarea value={form.inputBrief} onChange={(event) => setForm({ ...form, inputBrief: event.target.value })} className={styles.textarea} rows={4} />
                </Field>
                <Field label="반드시 포함">
                  <input value={form.mustInclude} onChange={(event) => setForm({ ...form, mustInclude: event.target.value })} className={styles.input} />
                </Field>
                <Field label="피해야 할 표현">
                  <input value={form.mustAvoid} onChange={(event) => setForm({ ...form, mustAvoid: event.target.value })} className={styles.input} />
                </Field>
                <Field label="원본 이미지 업로드" wide hint="draft 생성과 동시에 Nano Banana 1차 이미지 생성에 사용됩니다.">
                  <input type="file" accept="image/png,image/jpeg,image/webp" multiple onChange={handleFileChange} className={styles.fileInput} />
                </Field>
              </div>
              <div className={styles.assetPanel}>
                <div className={styles.assetHeader}>
                  <div>
                    <p className={styles.cardLabel}>Nano Banana</p>
                    <h3 className={styles.assetTitle}>API 키 설정</h3>
                  </div>
                  <span className={styles.assetCount}>{nanoBananaMaskedKey ? "saved" : "empty"}</span>
                </div>
                <Field label="Nano Banana API Key" wide hint="프론트에는 마스킹된 값만 표시됩니다.">
                  <input type="password" value={nanoBananaApiKey} onChange={(event) => setNanoBananaApiKey(event.target.value)} className={styles.input} placeholder="nb_..." />
                </Field>
                <label className={styles.variantToggle}>
                  <input
                    type="checkbox"
                    checked={form.applyImageVariant}
                    disabled={!canEnableVariant}
                    onChange={(event) => setForm({ ...form, applyImageVariant: event.target.checked, imageVariantProvider: event.target.checked ? "nano_banana" : "none" })}
                  />
                  <div>
                    <strong>draft 생성 시 1차 이미지 생성</strong>
                    <p className={styles.variantDescription}>원본 이미지 기반으로 먼저 이미지를 만들고, 텍스트는 다음 단계에서 별도로 편집합니다.</p>
                  </div>
                </label>
                <div className={styles.actions}>
                  <button type="button" onClick={handleSaveNanoBananaSetting} className={styles.primaryButton} disabled={isSavingNanoBanana || !nanoBananaApiKey.trim()}>
                    {isSavingNanoBanana ? "saving..." : "API 키 저장"}
                  </button>
                </div>
                <div className={styles.notice}>{nanoBananaMessage}</div>
              </div>
              <div className={styles.assetPanel}>
                <div className={styles.assetHeader}>
                  <div>
                    <p className={styles.cardLabel}>Registered Assets</p>
                    <h3 className={styles.assetTitle}>업로드한 원본 이미지</h3>
                  </div>
                  <span className={styles.assetCount}>{assets.length}개</span>
                </div>
                {assets.length > 0 ? (
                  <div className={styles.assetList}>
                    {assets.map((asset) => (
                      <div key={asset.assetId} className={styles.assetCard}>
                        <div>
                          <strong className={styles.assetName}>{asset.filename}</strong>
                          <p className={styles.assetMeta}>{asset.assetId} / {asset.contentType} / {formatBytes(asset.sizeBytes)} / {asset.status}</p>
                          {asset.localPreviewUrl ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img src={asset.localPreviewUrl} alt={asset.filename} className={styles.assetPreview} />
                          ) : null}
                        </div>
                        <button type="button" onClick={() => removeAsset(asset.assetId)} className={styles.ghostButton}>제거</button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className={styles.emptyState}>업로드한 원본 이미지가 없습니다.</p>
                )}
              </div>
              <div className={styles.notice}>{submitMessage}</div>
              <div className={styles.actions}>
                <button type="button" onClick={handleSubmit} className={styles.primaryButton} disabled={!canSubmit || isSubmitting}>
                  {isSubmitting ? "생성 중..." : "draft 생성"}
                </button>
              </div>
            </article>
          </>
        ) : null}

        {section === "content" ? (
          <article className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <p className={styles.cardLabel}>Content Ops</p>
                <h2 className={styles.panelTitle}>생성 이미지 검토와 재생성</h2>
              </div>
            </div>
            <div className={styles.queueList}>
              {pendingContents.map((item) => (
                <button key={item.content_id} type="button" className={styles.queueCard} onClick={() => void loadContentDetail(item.content_id)}>
                  <strong>{item.content_id}</strong>
                  <span>{item.platform}</span>
                  <span>{item.status}</span>
                </button>
              ))}
            </div>
            {contentDetail ? (
              <div className={styles.operationPanel}>
                <div className={styles.summaryGrid}>
                  <span>상태: {contentDetail.status}</span>
                  <span>플랫폼: {contentDetail.platform}</span>
                  <span>원본 자산 수: {contentDetail.uploaded_asset_ids.length}</span>
                  <span>생성 자산 수: {contentDetail.variant_asset_ids?.length ?? 0}</span>
                </div>
                <div className={styles.comparePanel}>
                  <CompareColumn title="Original Image" assets={contentAssets} emptyText="원본 이미지가 없습니다." />
                  <CompareColumn
                    title="Generated Image"
                    assets={variantAssets}
                    emptyText="생성 이미지가 없습니다."
                    selectedVariantAssetId={selectedVariantAssetId}
                    onSelectVariant={setSelectedVariantAssetId}
                  />
                </div>
                <div className={styles.actions}>
                  <button type="button" onClick={handleRegenerateImage} className={styles.ghostButton} disabled={isRegeneratingImage}>
                    {isRegeneratingImage ? "재생성 중..." : "이미지 재생성"}
                  </button>
                  <button type="button" onClick={handleApproveContent} className={styles.ghostButton}>승인</button>
                  <button type="button" onClick={handleRejectContent} className={styles.ghostButton}>반려</button>
                  <button type="button" onClick={() => void handleDeleteContent()} className={styles.dangerButton} disabled={contentDetail.status !== "draft"}>초안 삭제</button>
                  <button type="button" onClick={handlePublishContent} className={styles.primaryButton}>발행</button>
                </div>
              </div>
            ) : null}
            <div className={styles.notice}>{contentActionMessage}</div>
          </article>
        ) : null}

        {section === "overlay" ? (
          <article className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <p className={styles.cardLabel}>Overlay Editor</p>
                <h2 className={styles.panelTitle}>텍스트 오버레이 편집</h2>
              </div>
            </div>
            <div className={styles.queueList}>
              {pendingContents.map((item) => (
                <button key={item.content_id} type="button" className={styles.queueCard} onClick={() => void loadContentDetail(item.content_id)}>
                  <strong>{item.content_id}</strong>
                  <span>{item.platform}</span>
                  <span>{item.status}</span>
                </button>
              ))}
            </div>
            {contentDetail ? (
              <div className={styles.operationPanel}>
                <div className={styles.formGrid}>
                  <Field label="헤드라인" wide>
                    <input value={overlayHeadline} onChange={(event) => setOverlayHeadline(event.target.value)} className={styles.input} />
                  </Field>
                  <Field label="서브카피" wide>
                    <textarea value={overlaySubheadline} onChange={(event) => setOverlaySubheadline(event.target.value)} className={styles.textarea} rows={3} />
                  </Field>
                  <Field label="CTA" wide>
                    <input value={overlayCta} onChange={(event) => setOverlayCta(event.target.value)} className={styles.input} />
                  </Field>
                </div>
                <div className={styles.comparePanel}>
                  <CompareColumn
                    title="Generated Variants"
                    assets={variantAssets}
                    emptyText="생성 이미지가 없습니다."
                    selectedVariantAssetId={selectedVariantAssetId}
                    onSelectVariant={setSelectedVariantAssetId}
                  />
                  <div className={styles.compareColumn}>
                    <div className={styles.compareHeader}>
                      <p className={styles.cardLabel}>Overlay Preview</p>
                      <strong className={styles.assetName}>텍스트 미리보기</strong>
                    </div>
                    <div className={styles.overlayPreview}>
                      {selectedVariantAsset?.objectUrl ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={selectedVariantAsset.objectUrl} alt={selectedVariantAsset.filename} className={styles.overlayPreviewImage} />
                      ) : null}
                      <div className={styles.overlayPreviewShade} />
                      <div className={styles.overlayPreviewText}>
                        <h3 className={styles.overlayHeadline}>{overlayHeadline || "헤드라인을 입력하세요"}</h3>
                        <p className={styles.overlaySubheadline}>{overlaySubheadline || "서브카피를 입력하세요"}</p>
                        <span className={styles.overlayCta}>{overlayCta || "CTA"}</span>
                      </div>
                    </div>
                    <div className={styles.actions}>
                      <button type="button" onClick={handleSaveOverlay} className={styles.primaryButton} disabled={isSavingOverlay || !contentDetail}>
                        {isSavingOverlay ? "저장 중..." : "오버레이 저장"}
                      </button>
                      <button type="button" onClick={handleRegenerateImage} className={styles.ghostButton} disabled={isRegeneratingImage}>
                        {isRegeneratingImage ? "재생성 중..." : "이미지 재생성"}
                      </button>
                    </div>
                  </div>
                </div>
                <div className={styles.notice}>{overlayMessage}</div>
              </div>
            ) : null}
          </article>
        ) : null}

        {section === "reviews" ? (
          <article className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <p className={styles.cardLabel}>Review Actions</p>
                <h2 className={styles.panelTitle}>리뷰 답글 관리</h2>
              </div>
            </div>
            <div className={styles.queueList}>
              {reviewQueue.map((item) => (
                <button key={item.review_id} type="button" className={styles.queueCard} onClick={() => void handleSelectReview(item.review_id)}>
                  <strong>{item.review_id}</strong>
                  <span>{item.sensitivity}</span>
                  <span>{item.status}</span>
                </button>
              ))}
            </div>
            {reviewDetail ? (
              <div className={styles.operationPanel}>
                <p className={styles.cardDescription}>{reviewDetail.review_text}</p>
                <textarea value={reviewReplyText} onChange={(event) => setReviewReplyText(event.target.value)} className={styles.textarea} rows={4} />
                <div className={styles.actions}>
                  <button type="button" onClick={handleApproveReview} className={styles.primaryButton}>답글 승인</button>
                </div>
              </div>
            ) : null}
            <div className={styles.notice}>{reviewActionMessage}</div>
          </article>
        ) : null}

        {section === "ops" ? (
          <>
            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Operations</p>
                  <h2 className={styles.panelTitle}>작업과 리포트 현황</h2>
                </div>
              </div>
              <div className={styles.summaryGrid}>
                <span>작업 수: {jobs.length}</span>
                <span>리포트 수: {reports.length}</span>
                <span>발행 결과: {publishResults.length}</span>
                <span>draft 수: {pendingContents.filter((item) => item.status === "draft").length}</span>
              </div>
              <div className={styles.actions}>
                <button type="button" onClick={handleGenerateReport} className={styles.primaryButton}>월간 리포트 생성</button>
                <button type="button" onClick={() => void loadOperations()} className={styles.ghostButton} disabled={isRefreshingOps}>
                  {isRefreshingOps ? "새로고침 중..." : "새로고침"}
                </button>
              </div>
              <div className={styles.notice}>{reportMessage}</div>
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
                      <strong className={styles.draftTitle}>{draft.targetCountry} / {draft.platform}</strong>
                      <p className={styles.cardDescription}>{draft.message}</p>
                      <p className={styles.assetMeta}>{draft.contentId}</p>
                    </div>
                  ))
                ) : (
                  <p className={styles.emptyState}>최근 생성 결과가 없습니다.</p>
                )}
              </div>
            </article>
            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.cardLabel}>Publish Results</p>
                  <h2 className={styles.panelTitle}>발행 카드 결과</h2>
                </div>
              </div>
              <div className={styles.publishResultGrid}>
                {publishResults.length > 0 ? (
                  publishResults.slice(0, 6).map((result) => (
                    <div key={result.publish_result_id} className={styles.publishResultCard}>
                      {result.thumbnail_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={result.thumbnail_url} alt={result.title ?? result.publish_result_id} className={styles.publishResultImage} />
                      ) : (
                        <div className={styles.publishResultFallback}>NO THUMBNAIL</div>
                      )}
                      <div className={styles.publishResultBody}>
                        <strong className={styles.assetName}>{result.title ?? result.publish_result_id}</strong>
                        <p className={styles.assetMeta}>{result.status} · {result.channel}</p>
                        <p className={styles.cardDescription}>{result.caption_preview ?? "캡션 미리보기가 없습니다."}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className={styles.emptyState}>발행 결과가 없습니다.</p>
                )}
              </div>
            </article>
          </>
        ) : null}
      </section>
    </main>
  );
}

function titleForSection(section: MerchantDashboardSection) {
  if (section === "compose") return "Draft 생성";
  if (section === "content") return "콘텐츠 운영";
  if (section === "overlay") return "오버레이 편집";
  if (section === "reviews") return "리뷰 응대";
  return "운영 현황";
}

function CompareColumn({
  title,
  assets,
  emptyText,
  selectedVariantAssetId,
  onSelectVariant,
}: {
  title: string;
  assets: ContentPreviewAsset[];
  emptyText: string;
  selectedVariantAssetId?: string;
  onSelectVariant?: (assetId: string) => void;
}) {
  return (
    <div className={styles.compareColumn}>
      <div className={styles.compareHeader}>
        <p className={styles.cardLabel}>{title}</p>
      </div>
      {assets.length > 0 ? (
        <div className={styles.contentPreviewGrid}>
          {assets.map((asset) => (
            <div
              key={asset.asset_id}
              className={`${styles.contentPreviewCard} ${
                selectedVariantAssetId && selectedVariantAssetId === asset.asset_id ? styles.contentPreviewCardSelected : ""
              }`}
            >
              {asset.objectUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={asset.objectUrl} alt={asset.filename} className={styles.contentPreviewImage} />
              ) : (
                <div className={styles.contentPreviewFallback}>NO PREVIEW</div>
              )}
              <strong className={styles.assetName}>{asset.filename}</strong>
              <p className={styles.assetMeta}>{asset.asset_id}</p>
              {onSelectVariant ? (
                <div className={styles.actions}>
                  <button type="button" className={styles.ghostButton} onClick={() => onSelectVariant(asset.asset_id)}>
                    {selectedVariantAssetId === asset.asset_id ? "선택됨" : "선택"}
                  </button>
                </div>
              ) : null}
            </div>
          ))}
        </div>
      ) : (
        <div className={styles.compareEmpty}>{emptyText}</div>
      )}
    </div>
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
