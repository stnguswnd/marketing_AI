"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { clearAuthSession, readAuthSession, writeAuthSession } from "@/lib/auth";
import { listTestAccounts, login } from "@/lib/api";

import styles from "./home-hub.module.css";

const routes = [
  {
    href: "/merchant",
    eyebrow: "Merchant",
    title: "점주 작업 화면",
    description: "콘텐츠 요청, 승인, 발행, 리뷰 대응까지 점주가 직접 처리한다.",
  },
  {
    href: "/admin",
    eyebrow: "Admin",
    title: "운영 관리자 화면",
    description: "등록된 점주 목록, 감사 로그, 관측 데이터를 관리한다.",
  },
];

export function HomeHub() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [accounts, setAccounts] = useState<Awaited<ReturnType<typeof listTestAccounts>>["items"]>([]);
  const [session, setSession] = useState<ReturnType<typeof readAuthSession>>(null);
  const [message, setMessage] = useState("test1~test4 계정으로 바로 로그인할 수 있습니다.");
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("test1@email.com");
  const [password, setPassword] = useState("12345678");

  useEffect(() => {
    setMounted(true);
    setSession(readAuthSession());
    void listTestAccounts()
      .then((response) => setAccounts(response.items))
      .catch((error) => setMessage(error instanceof Error ? error.message : "테스트 계정을 불러오지 못했습니다."));
  }, []);

  async function handleLogin(targetEmail: string, targetPassword = "12345678") {
    setIsLoading(true);
    setMessage("로그인 중입니다.");
    try {
      const auth = await login({ email: targetEmail, password: targetPassword });
      writeAuthSession(auth);
      setSession(auth);
      setMessage(`${auth.displayName} 계정으로 로그인했습니다.`);
      router.push(auth.role === "admin" ? "/admin" : "/merchant");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "로그인에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout() {
    clearAuthSession();
    setSession(null);
    setMessage("로그아웃했습니다.");
  }

  return (
    <main className={styles.page}>
      <section className={styles.shell}>
        <header className={styles.hero}>
          <p className={styles.eyebrow}>Harness Frontend</p>
          <h1 className={styles.title}>test1~test4 계정으로 진입하는 작업 허브</h1>
          <p className={styles.description}>
            PostgreSQL 목업 DB에 들어간 관리자 1명과 점주 3명의 계정으로 바로 로그인하고, 역할별 화면을
            분리해서 검증할 수 있다.
          </p>
          <div className={styles.sessionBar}>
            <span>{mounted && session ? `${session.displayName} · ${session.role}` : "로그인 전"}</span>
            {session?.merchantName ? <span>{session.merchantName}</span> : null}
            <button type="button" onClick={handleLogout} className={styles.logoutButton} disabled={!session}>
              로그아웃
            </button>
          </div>
        </header>

        <section className={styles.loginPanel}>
          <div className={styles.loginCopy}>
            <p className={styles.cardEyebrow}>Login</p>
            <h2 className={styles.cardTitle}>로그인 화면</h2>
            <p className={styles.cardDescription}>
              관리자 `test1`, 점주 `test2~test4` 계정으로 바로 진입할 수 있다. 비밀번호는 모두 `12345678` 이다.
            </p>
          </div>
          <div className={styles.loginForm}>
            <label className={styles.field}>
              <span className={styles.fieldLabel}>이메일</span>
              <input value={email} onChange={(event) => setEmail(event.target.value)} className={styles.input} />
            </label>
            <label className={styles.field}>
              <span className={styles.fieldLabel}>비밀번호</span>
              <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" className={styles.input} />
            </label>
            <button type="button" className={styles.loginButton} onClick={() => void handleLogin(email, password)} disabled={isLoading}>
              {isLoading ? "로그인 중..." : "로그인"}
            </button>
          </div>
        </section>

        <section className={styles.accountGrid}>
          {accounts.map((account) => (
            <article key={account.email} className={styles.accountCard}>
              <div className={styles.accountHeader}>
                <Image
                  src={account.profile_image_url}
                  alt={account.display_name}
                  className={styles.avatar}
                  width={56}
                  height={56}
                />
                <div>
                  <p className={styles.cardEyebrow}>{account.role}</p>
                  <h2 className={styles.cardTitle}>{account.display_name}</h2>
                </div>
              </div>
              <p className={styles.cardDescription}>
                {account.email}
                {account.merchant_name ? ` · ${account.merchant_name}` : ""}
              </p>
              <p className={styles.cardDescription}>비밀번호: 12345678</p>
              <button type="button" className={styles.loginButton} onClick={() => void handleLogin(account.email)} disabled={isLoading}>
                {isLoading ? "로그인 중..." : "이 계정으로 로그인"}
              </button>
            </article>
          ))}
        </section>

        <p className={styles.message}>{message}</p>

        <section className={styles.grid}>
          {routes.map((route) => (
            <Link key={route.href} href={route.href} className={styles.card}>
              <p className={styles.cardEyebrow}>{route.eyebrow}</p>
              <h2 className={styles.cardTitle}>{route.title}</h2>
              <p className={styles.cardDescription}>{route.description}</p>
              <span className={styles.cardAction}>
                {mounted && session ? "바로 이동" : "로그인 후 이동"}
              </span>
            </Link>
          ))}
        </section>
      </section>
    </main>
  );
}
