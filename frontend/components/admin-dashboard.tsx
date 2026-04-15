"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { readAuthSession } from "@/lib/auth";
import {
  fetchObservabilitySummary,
  listAuditLogs,
  listMerchantSummaries,
  listObservabilityRequests,
} from "@/lib/api";

import styles from "./admin-dashboard.module.css";

export function AdminDashboard() {
  const [mounted, setMounted] = useState(false);
  const [authSession, setAuthSession] = useState<ReturnType<typeof readAuthSession>>(null);
  const [merchantItems, setMerchantItems] = useState<Awaited<ReturnType<typeof listMerchantSummaries>>["items"]>([]);
  const [auditLogs, setAuditLogs] = useState<Awaited<ReturnType<typeof listAuditLogs>>["items"]>([]);
  const [requestTraces, setRequestTraces] = useState<Awaited<ReturnType<typeof listObservabilityRequests>>["items"]>([]);
  const [observabilitySummary, setObservabilitySummary] = useState<Awaited<ReturnType<typeof fetchObservabilitySummary>> | null>(null);
  const [statusMessage, setStatusMessage] = useState("관리자 화면은 등록된 점포와 전체 플랫폼 상태를 관리합니다.");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setMounted(true);
    const session = readAuthSession();
    setAuthSession(session);
    if (session?.role === "admin") {
      void loadDashboard();
    }
  }, []);

  if (!mounted || !authSession || authSession.role !== "admin") {
    return (
      <main className={styles.page}>
        <section className={styles.shell}>
          <section className={styles.panel}>
            <p className={styles.cardLabel}>Admin Access</p>
            <h1 className={styles.panelTitle}>{mounted ? "관리자 계정으로 로그인해야 합니다." : "관리자 화면을 준비하는 중입니다."}</h1>
            <p className={styles.helperText}>
              {mounted ? "`test1@email.com` 계정으로 로그인한 뒤 관리자 화면에 접근하세요." : "세션을 확인하고 있습니다."}
            </p>
            <nav className={styles.actions}>
              <Link href="/" className={styles.linkButton}>
                홈으로 이동
              </Link>
            </nav>
          </section>
        </section>
      </main>
    );
  }

  async function loadDashboard() {
    setIsLoading(true);
    setStatusMessage("관리자용 점포/감사/관측 데이터를 불러오는 중입니다.");
    try {
      const [merchants, audit, traces, summary] = await Promise.all([
        listMerchantSummaries(),
        listAuditLogs(),
        listObservabilityRequests(),
        fetchObservabilitySummary(),
      ]);
      setMerchantItems(merchants.items);
      setAuditLogs(audit.items);
      setRequestTraces(traces.items);
      setObservabilitySummary(summary);
      setStatusMessage("관리자 데이터를 갱신했습니다.");
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "관리자 데이터를 불러오지 못했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className={styles.page}>
      <section className={styles.shell}>
        <header className={styles.hero}>
          <div>
            <p className={styles.eyebrow}>Admin Workspace</p>
            <h1 className={styles.title}>관리자 운영 화면</h1>
            <p className={styles.description}>
              관리자는 등록된 점주와 플랫폼 상태를 관리한다. 콘텐츠 승인과 발행 실무는 점주 화면으로 이동했다.
            </p>
            <p className={styles.description}>현재 로그인: {authSession?.displayName ?? "미로그인"} · {authSession?.email ?? "-"}</p>
          </div>
          <nav className={styles.actions}>
            <Link href="/" className={styles.linkButton}>
              홈
            </Link>
            <Link href="/merchant" className={styles.linkButton}>
              점주 화면
            </Link>
          </nav>
        </header>

        <section className={styles.queueGrid}>
          <article className={styles.card}>
            <p className={styles.cardLabel}>Merchants</p>
            <strong className={styles.count}>{merchantItems.length}</strong>
            <p className={styles.cardDescription}>등록된 점포 수</p>
          </article>
          <article className={styles.card}>
            <p className={styles.cardLabel}>Audit Logs</p>
            <strong className={styles.count}>{auditLogs.length}</strong>
            <p className={styles.cardDescription}>전체 감사 이벤트 수</p>
          </article>
          <article className={styles.card}>
            <p className={styles.cardLabel}>Requests</p>
            <strong className={styles.count}>{observabilitySummary?.total_requests ?? 0}</strong>
            <p className={styles.cardDescription}>최근 요청 추적 수</p>
          </article>
        </section>
        <p className={styles.helperText}>{statusMessage}</p>

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.cardLabel}>Merchant Directory</p>
              <h2 className={styles.panelTitle}>등록된 점주 현황</h2>
            </div>
            <button type="button" onClick={() => void loadDashboard()} className={styles.secondaryButton} disabled={isLoading}>
              {isLoading ? "갱신 중..." : "새로고침"}
            </button>
          </div>

          <div className={styles.listStack}>
            {merchantItems.length > 0 ? (
              merchantItems.map((item) => (
                <div key={item.merchant_id} className={styles.queueItemStatic}>
                  <span>{item.merchant_id}</span>
                  <span>콘텐츠 {item.content_count}</span>
                  <span>리뷰 {item.review_count}</span>
                </div>
              ))
            ) : (
              <p className={styles.helperText}>등록된 점포 데이터가 없습니다.</p>
            )}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.cardLabel}>Merchant Detail Snapshot</p>
              <h2 className={styles.panelTitle}>점포별 운영 지표</h2>
            </div>
          </div>

          <div className={styles.summaryGrid}>
            {merchantItems.slice(0, 6).map((item) => (
              <div key={item.merchant_id} className={styles.summaryCard}>
                <span className={styles.cardLabel}>{item.merchant_id}</span>
                <strong>대기 콘텐츠 {item.pending_content_count}</strong>
                <strong>승인 콘텐츠 {item.approved_content_count}</strong>
                <strong>대기 리뷰 {item.pending_review_count}</strong>
                <strong>자산 {item.asset_count}</strong>
                <strong>리포트 {item.report_count}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.cardLabel}>Observability</p>
              <h2 className={styles.panelTitle}>감사 로그와 요청 추적</h2>
            </div>
          </div>

          {observabilitySummary ? (
            <div className={styles.summaryGrid}>
              <div className={styles.summaryCard}>
                <span className={styles.cardLabel}>Requests</span>
                <strong>{observabilitySummary.total_requests}</strong>
              </div>
              <div className={styles.summaryCard}>
                <span className={styles.cardLabel}>Success</span>
                <strong>{observabilitySummary.status_counts["200"] ?? 0}</strong>
              </div>
              <div className={styles.summaryCard}>
                <span className={styles.cardLabel}>Top Path</span>
                <strong>{Object.entries(observabilitySummary.path_counts)[0]?.[0] ?? "-"}</strong>
              </div>
            </div>
          ) : null}

          <div className={styles.observabilityGrid}>
            <div className={styles.inlineSection}>
              <p className={styles.cardLabel}>Audit Logs</p>
              <div className={styles.listStack}>
                {auditLogs.slice(0, 8).map((item) => (
                  <div key={item.audit_log_id} className={styles.queueItemStatic}>
                    <span>{item.action}</span>
                    <span>{item.resource_type}</span>
                    <span>{item.status}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className={styles.inlineSection}>
              <p className={styles.cardLabel}>Request Traces</p>
              <div className={styles.listStack}>
                {requestTraces.slice(0, 8).map((item) => (
                  <div key={item.request_id} className={styles.queueItemStatic}>
                    <span>{item.path}</span>
                    <span>{item.status_code}</span>
                    <span>{item.duration_ms}ms</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
