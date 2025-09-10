// 喫煙習慣に関する型定義

// 喫煙状況の列挙型
export type SmokingStatus = 'smoker' | 'non_smoker' | 'ex_smoker';

// タバコの種類の列挙型  
export type CigaretteType = 'traditional' | 'electronic' | 'both';

// 禁煙意向の列挙型
export type QuitIntention = 'planning' | 'considering' | 'not_interested';

// 喫煙パターンの列挙型
export type SmokingPatternItem = 'morning' | 'afternoon' | 'evening' | 'night';

// 喫煙習慣データ型
export interface SmokingHabitsData {
  session_id?: string;
  smoking_status: SmokingStatus;
  daily_cigarettes?: number;
  smoking_years?: number;
  quit_date?: string; // YYYY-MM形式
  cigarette_type?: CigaretteType;
  tar_content?: number;
  nicotine_content?: number;
  quit_intention?: QuitIntention;
  smoking_pattern?: SmokingPatternItem[];
}

// API リクエスト型
export interface SmokingHabitsRequest extends SmokingHabitsData {}

// API レスポンス型
export interface SmokingHabitsResponse {
  success: true;
  data: {
    questionnaire_id: string;
    session_id: string;
    submitted_at: string;
    smoking_habits: SmokingHabitsData;
  };
}

// API エラーレスポンス型
export interface SmokingHabitsError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Array<{
      field: string;
      message: string;
    }>;
  };
}

// バリデーション結果型
export interface ValidationResult {
  isValid: boolean;
  errors: Array<{
    field: keyof SmokingHabitsData | 'general';
    message: string;
  }>;
}

// フォーム状態型
export interface SmokingHabitsFormState extends SmokingHabitsData {
  isSubmitting: boolean;
  errors: Record<string, string>;
}

// 選択肢の型
export interface SelectOption {
  value: string;
  label: string;
}

// フォーム用の選択肢定義
export const smokingStatusOptions: SelectOption[] = [
  { value: 'non_smoker', label: '非喫煙者' },
  { value: 'smoker', label: '現在喫煙者' },
  { value: 'ex_smoker', label: '元喫煙者' },
];

export const cigaretteTypeOptions: SelectOption[] = [
  { value: 'traditional', label: '紙たばこ' },
  { value: 'electronic', label: '電子タバコ' },
  { value: 'both', label: '両方' },
];

export const quitIntentionOptions: SelectOption[] = [
  { value: 'planning', label: '禁煙を計画中' },
  { value: 'considering', label: '禁煙を検討中' },
  { value: 'not_interested', label: '禁煙は考えていない' },
];

export const smokingPatternOptions: SelectOption[] = [
  { value: 'morning', label: '朝' },
  { value: 'afternoon', label: '昼' },
  { value: 'evening', label: '夕方' },
  { value: 'night', label: '夜' },
];