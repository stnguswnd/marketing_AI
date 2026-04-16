"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

import styles from "./merchant-shell.module.css";

const navItems = [
  { href: "/merchant/compose", title: "Draft 생성", description: "원본 업로드와 1차 이미지 생성" },
  { href: "/merchant/content", title: "콘텐츠 운영", description: "생성 이미지 검토, 재생성, 승인" },
  { href: "/merchant/overlay", title: "오버레이 편집", description: "텍스트 편집과 카드 미리보기" },
  { href: "/merchant/reviews", title: "리뷰 응대", description: "리뷰 답글 승인 관리" },
  { href: "/merchant/ops", title: "운영 현황", description: "리포트와 작업 상태 확인" },
];

export function MerchantShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <p className={styles.eyebrow}>Merchant Workspace</p>
          <h1 className={styles.title}>점주 운영</h1>
        </div>
        <nav className={styles.nav}>
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`${styles.navLink} ${active ? styles.navLinkActive : ""}`}
              >
                <span className={styles.navTitle}>{item.title}</span>
                <span className={styles.navDesc}>{item.description}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className={styles.main}>{children}</main>
    </div>
  );
}
