export type Currency = "MZN" | "USD" | "EUR" | "BRL" | "GBP" | "ZAR";

export const CURRENCY_LABELS: Record<Currency, string> = {
  MZN: "Metical",
  USD: "Dólar Americano",
  EUR: "Euro",
  BRL: "Real Brasileiro",
  GBP: "Libra Esterlina",
  ZAR: "Rand Sul-Africano",
};

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  birth_date: string | null;
  country: string | null;
  city: string | null;
  profile_photo_url: string | null;
  status: "active" | "blocked" | "pending_verification";
  email_verified: boolean;
  has_transaction_pin: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface WalletBalance {
  currency: Currency;
  balance: string;
}

export interface Wallet {
  id: string;
  balances: WalletBalance[];
}

export type DepositProvider = "mpesa" | "emola";
export type DepositStatus = "pending" | "confirmed" | "failed" | "expired";

export interface Deposit {
  id: string;
  provider: DepositProvider;
  reference_code: string;
  amount: string;
  currency: Currency;
  status: DepositStatus;
  created_at: string;
  confirmed_at: string | null;
}

export type TransactionType = "deposit" | "conversion" | "withdrawal" | "adjustment";
export type TransactionStatus = "pending" | "completed" | "failed" | "cancelled";

export interface Transaction {
  id: string;
  type: TransactionType;
  status: TransactionStatus;
  amount: string;
  currency: Currency;
  exchange_rate: string | null;
  source_currency: Currency | null;
  source_amount: string | null;
  notes: string | null;
  created_at: string;
}

export interface TransactionListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Transaction[];
}
