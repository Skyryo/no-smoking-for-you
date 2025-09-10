import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Select,
  MenuItem,
  Checkbox,
  FormGroup,
  Button,
  Alert,
  LinearProgress,
  Divider,
  Slider,
} from '@mui/material';
import { Save as SaveIcon, Send as SendIcon } from '@mui/icons-material';

import type {
  SmokingHabitsFormState,
  SmokingStatus,
  CigaretteType,
  QuitIntention,
  SmokingPatternItem,
  ValidationResult,
} from '../types/smokingHabits';
import {
  smokingStatusOptions,
  cigaretteTypeOptions,
  quitIntentionOptions,
  smokingPatternOptions,
} from '../types/smokingHabits';
import { smokingHabitsApi, SmokingHabitsApiError } from '../services/api';

interface QuestionnaireFormProps {
  sessionId?: string;
  onSubmitSuccess?: (result: any) => void;
  onSubmitError?: (error: any) => void;
}

const QuestionnaireForm: React.FC<QuestionnaireFormProps> = ({
  sessionId,
  onSubmitSuccess,
  onSubmitError,
}) => {
  const [formState, setFormState] = useState<SmokingHabitsFormState>({
    session_id: sessionId,
    smoking_status: 'non_smoker',
    isSubmitting: false,
    errors: {},
  });

  const [submitResult, setSubmitResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  // バリデーション関数
  const validateForm = (): ValidationResult => {
    const errors: ValidationResult['errors'] = [];

    // 喫煙者の場合の必須項目チェック
    if (formState.smoking_status === 'smoker') {
      if (!formState.daily_cigarettes) {
        errors.push({ field: 'daily_cigarettes', message: '1日の喫煙本数は必須です' });
      } else if (formState.daily_cigarettes < 1 || formState.daily_cigarettes > 100) {
        errors.push({ field: 'daily_cigarettes', message: '1日の喫煙本数は1-100本で入力してください' });
      }

      if (!formState.cigarette_type) {
        errors.push({ field: 'cigarette_type', message: 'タバコの種類は必須です' });
      }
    }

    // 喫煙者または元喫煙者の場合の喫煙年数チェック
    if (formState.smoking_status === 'smoker' || formState.smoking_status === 'ex_smoker') {
      if (!formState.smoking_years) {
        errors.push({ field: 'smoking_years', message: '喫煙年数は必須です' });
      } else if (formState.smoking_years < 1 || formState.smoking_years > 80) {
        errors.push({ field: 'smoking_years', message: '喫煙年数は1-80年で入力してください' });
      }
    }

    // 元喫煙者の場合の禁煙開始時期チェック
    if (formState.smoking_status === 'ex_smoker') {
      if (!formState.quit_date) {
        errors.push({ field: 'quit_date', message: '禁煙開始時期は必須です' });
      } else if (!/^\d{4}-\d{2}$/.test(formState.quit_date)) {
        errors.push({ field: 'quit_date', message: '禁煙開始時期はYYYY-MM形式で入力してください' });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  };

  // フォーム値の更新
  const updateFormField = (field: keyof SmokingHabitsFormState, value: any) => {
    setFormState(prev => ({
      ...prev,
      [field]: value,
      errors: {
        ...prev.errors,
        [field]: '', // エラーをクリア
      },
    }));

    // 喫煙状況が変わった場合、関連項目をリセット
    if (field === 'smoking_status') {
      setFormState(prev => ({
        ...prev,
        smoking_status: value,
        daily_cigarettes: undefined,
        smoking_years: undefined,
        quit_date: undefined,
        cigarette_type: undefined,
        tar_content: undefined,
        nicotine_content: undefined,
        quit_intention: undefined,
        smoking_pattern: undefined,
        errors: {},
      }));
    }
  };

  // パターンの選択/解除
  const toggleSmokingPattern = (pattern: SmokingPatternItem) => {
    const currentPatterns = formState.smoking_pattern || [];
    const newPatterns = currentPatterns.includes(pattern)
      ? currentPatterns.filter(p => p !== pattern)
      : [...currentPatterns, pattern];
    
    updateFormField('smoking_pattern', newPatterns);
  };

  // フォーム送信
  const handleSubmit = async () => {
    const validation = validateForm();
    
    if (!validation.isValid) {
      const errorMap: Record<string, string> = {};
      validation.errors.forEach(error => {
        errorMap[error.field] = error.message;
      });
      setFormState(prev => ({ ...prev, errors: errorMap }));
      return;
    }

    setFormState(prev => ({ ...prev, isSubmitting: true }));
    setSubmitResult(null);

    try {
      const response = await smokingHabitsApi.submitSmokingHabits({
        session_id: formState.session_id,
        smoking_status: formState.smoking_status,
        daily_cigarettes: formState.daily_cigarettes,
        smoking_years: formState.smoking_years,
        quit_date: formState.quit_date,
        cigarette_type: formState.cigarette_type,
        tar_content: formState.tar_content,
        nicotine_content: formState.nicotine_content,
        quit_intention: formState.quit_intention,
        smoking_pattern: formState.smoking_pattern,
      });

      setSubmitResult({
        success: true,
        message: '喫煙習慣の情報を正常に保存しました',
      });

      if (onSubmitSuccess) {
        onSubmitSuccess(response.data);
      }
    } catch (error) {
      let errorMessage = '送信中にエラーが発生しました';
      
      if (error instanceof SmokingHabitsApiError) {
        errorMessage = error.message;
        
        // フィールド別エラーがある場合は表示
        if (error.errorResponse.error.details) {
          const errorMap: Record<string, string> = {};
          error.errorResponse.error.details.forEach(detail => {
            errorMap[detail.field] = detail.message;
          });
          setFormState(prev => ({ ...prev, errors: errorMap }));
        }
      }

      setSubmitResult({
        success: false,
        message: errorMessage,
      });

      if (onSubmitError) {
        onSubmitError(error);
      }
    } finally {
      setFormState(prev => ({ ...prev, isSubmitting: false }));
    }
  };

  const showSmokingDetails = formState.smoking_status === 'smoker';
  const showQuitDetails = formState.smoking_status === 'ex_smoker';
  const showYearsOfSmoking = formState.smoking_status === 'smoker' || formState.smoking_status === 'ex_smoker';

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          喫煙習慣に関する問診
        </Typography>
        
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          あなたの喫煙習慣について教えてください。すべての情報は健康予測の精度向上のために使用されます。
        </Typography>

        {/* 送信結果表示 */}
        {submitResult && (
          <Alert 
            severity={submitResult.success ? 'success' : 'error'} 
            sx={{ mb: 3 }}
          >
            {submitResult.message}
          </Alert>
        )}

        {/* 送信中のプログレス */}
        {formState.isSubmitting && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress />
            <Typography variant="body2" align="center" sx={{ mt: 1 }}>
              送信中...
            </Typography>
          </Box>
        )}

        <Box component="form" noValidate>
          {/* 喫煙状況 */}
          <FormControl component="fieldset" fullWidth sx={{ mb: 3 }}>
            <FormLabel component="legend" required>
              現在の喫煙状況
            </FormLabel>
            <RadioGroup
              value={formState.smoking_status}
              onChange={(e) => updateFormField('smoking_status', e.target.value as SmokingStatus)}
            >
              {smokingStatusOptions.map((option) => (
                <FormControlLabel
                  key={option.value}
                  value={option.value}
                  control={<Radio />}
                  label={option.label}
                />
              ))}
            </RadioGroup>
          </FormControl>

          {/* 喫煙年数（喫煙者・元喫煙者の場合） */}
          {showYearsOfSmoking && (
            <TextField
              fullWidth
              label="喫煙年数"
              type="number"
              value={formState.smoking_years || ''}
              onChange={(e) => updateFormField('smoking_years', parseInt(e.target.value) || undefined)}
              error={!!formState.errors.smoking_years}
              helperText={formState.errors.smoking_years || '何年間喫煙していた/しているかを入力してください（1-80年）'}
              required
              inputProps={{ min: 1, max: 80 }}
              sx={{ mb: 3 }}
            />
          )}

          {/* 禁煙開始時期（元喫煙者の場合） */}
          {showQuitDetails && (
            <TextField
              fullWidth
              label="禁煙開始時期"
              placeholder="2023-06"
              value={formState.quit_date || ''}
              onChange={(e) => updateFormField('quit_date', e.target.value)}
              error={!!formState.errors.quit_date}
              helperText={formState.errors.quit_date || 'YYYY-MM形式で入力してください（例：2023-06）'}
              required
              sx={{ mb: 3 }}
            />
          )}

          {/* 現在喫煙者の詳細項目 */}
          {showSmokingDetails && (
            <>
              <Divider sx={{ my: 3 }}>
                <Typography variant="h6" color="text.secondary">
                  喫煙詳細
                </Typography>
              </Divider>

              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                <Box>
                  <TextField
                    fullWidth
                    label="1日の喫煙本数"
                    type="number"
                    value={formState.daily_cigarettes || ''}
                    onChange={(e) => updateFormField('daily_cigarettes', parseInt(e.target.value) || undefined)}
                    error={!!formState.errors.daily_cigarettes}
                    helperText={formState.errors.daily_cigarettes || '1日あたりの本数（1-100本）'}
                    required
                    inputProps={{ min: 1, max: 100 }}
                  />
                </Box>

                <Box>
                  <FormControl fullWidth required error={!!formState.errors.cigarette_type}>
                    <FormLabel>タバコの種類</FormLabel>
                    <Select
                      value={formState.cigarette_type || ''}
                      onChange={(e) => updateFormField('cigarette_type', e.target.value as CigaretteType)}
                      displayEmpty
                    >
                      <MenuItem value="">選択してください</MenuItem>
                      {cigaretteTypeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                    {formState.errors.cigarette_type && (
                      <Typography variant="caption" color="error" sx={{ mt: 0.5 }}>
                        {formState.errors.cigarette_type}
                      </Typography>
                    )}
                  </FormControl>
                </Box>

                <Box>
                  <Box>
                    <Typography gutterBottom>タール含有量（mg）</Typography>
                    <Slider
                      value={formState.tar_content || 12}
                      onChange={(_, value) => updateFormField('tar_content', value as number)}
                      min={1}
                      max={25}
                      step={1}
                      marks={[
                        { value: 1, label: '1mg' },
                        { value: 12, label: '12mg' },
                        { value: 25, label: '25mg' },
                      ]}
                      valueLabelDisplay="on"
                    />
                  </Box>
                </Box>

                <Box>
                  <Box>
                    <Typography gutterBottom>ニコチン含有量（mg）</Typography>
                    <Slider
                      value={formState.nicotine_content || 1.0}
                      onChange={(_, value) => updateFormField('nicotine_content', value as number)}
                      min={0.1}
                      max={3.0}
                      step={0.1}
                      marks={[
                        { value: 0.1, label: '0.1mg' },
                        { value: 1.0, label: '1.0mg' },
                        { value: 3.0, label: '3.0mg' },
                      ]}
                      valueLabelDisplay="on"
                    />
                  </Box>
                </Box>
              </Box>

              {/* 喫煙パターン */}
              <Box sx={{ mt: 3 }}>
                <FormLabel component="legend">喫煙時間帯（複数選択可）</FormLabel>
                <FormGroup row sx={{ mt: 1 }}>
                  {smokingPatternOptions.map((option) => (
                    <FormControlLabel
                      key={option.value}
                      control={
                        <Checkbox
                          checked={(formState.smoking_pattern || []).includes(option.value as SmokingPatternItem)}
                          onChange={() => toggleSmokingPattern(option.value as SmokingPatternItem)}
                        />
                      }
                      label={option.label}
                    />
                  ))}
                </FormGroup>
              </Box>

              {/* 禁煙意向 */}
              <FormControl fullWidth sx={{ mt: 3 }}>
                <FormLabel>禁煙への意向</FormLabel>
                <Select
                  value={formState.quit_intention || ''}
                  onChange={(e) => updateFormField('quit_intention', e.target.value as QuitIntention)}
                  displayEmpty
                >
                  <MenuItem value="">選択してください</MenuItem>
                  {quitIntentionOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </>
          )}

          {/* 送信ボタン */}
          <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleSubmit}
              disabled={formState.isSubmitting || submitResult?.success}
              startIcon={submitResult?.success ? <SaveIcon /> : <SendIcon />}
              sx={{ minWidth: 200 }}
            >
              {formState.isSubmitting 
                ? '送信中...' 
                : submitResult?.success 
                  ? '保存済み' 
                  : '問診結果を送信'
              }
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default QuestionnaireForm;
