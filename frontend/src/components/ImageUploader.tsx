import React, { useState, useRef, DragEvent, ChangeEvent } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
} from "@mui/material";
import { CloudUpload as CloudUploadIcon } from "@mui/icons-material";

interface ImageUploaderProps {
  onUploadSuccess: (result: UploadImageResponse["data"]) => void;
  onUploadError: (error: UploadImageError["error"]) => void;
  sessionId?: string;
  disabled?: boolean;
}

interface ImageUploaderState {
  dragOver: boolean;
  selectedFile: File | null;
  previewUrl: string | null;
  uploading: boolean;
  progress: number;
  currentStage: string;
  error: string | null;
}

interface UploadImageResponse {
  success: boolean;
  data?: {
    imageId: string;
    sessionId: string;
    uploadedAt: string;
    originalUrl: string;
    metadata: {
      filename: string;
      contentType: string;
      size: number;
      dimensions: {
        width: number;
        height: number;
      };
    };
  };
}

interface UploadImageError {
  success: boolean;
  error: {
    code: string;
    message: string;
    details?: any;
  };
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  onUploadSuccess,
  onUploadError,
  sessionId,
  disabled = false,
}) => {
  const [state, setState] = useState<ImageUploaderState>({
    dragOver: false,
    selectedFile: null,
    previewUrl: null,
    uploading: false,
    progress: 0,
    currentStage: "",
    error: null,
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  // File validation constants
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const MIN_FILE_SIZE = 1024; // 1KB
  const ALLOWED_TYPES = ["image/jpeg", "image/png"];

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return "JPEG またはPNG形式のファイルを選択してください";
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return `ファイルサイズが大きすぎます（最大: ${formatFileSize(MAX_FILE_SIZE)}）`;
    }
    if (file.size < MIN_FILE_SIZE) {
      return "ファイルサイズが小さすぎます";
    }

    return null; // Validation passed
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const generatePreview = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.readAsDataURL(file);
    });
  };

  const handleFileSelect = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setState(prev => ({ ...prev, error: validationError, selectedFile: null, previewUrl: null }));
      return;
    }

    try {
      const previewUrl = await generatePreview(file);
      setState(prev => ({
        ...prev,
        selectedFile: file,
        previewUrl,
        error: null,
      }));
    } catch (error) {
      setState(prev => ({ ...prev, error: "プレビューの生成に失敗しました" }));
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setState(prev => ({ ...prev, dragOver: false }));

    if (disabled || state.uploading) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled && !state.uploading) {
      setState(prev => ({ ...prev, dragOver: true }));
    }
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setState(prev => ({ ...prev, dragOver: false }));
  };

  const handleClick = () => {
    if (!disabled && !state.uploading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleClear = () => {
    setState(prev => ({
      ...prev,
      selectedFile: null,
      previewUrl: null,
      error: null,
      progress: 0,
      currentStage: "",
    }));

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleUpload = async () => {
    if (!state.selectedFile) return;

    setState(prev => ({ ...prev, uploading: true, progress: 0, currentStage: "準備中...", error: null }));

    try {
      // Simulate different stages of upload
      setState(prev => ({ ...prev, progress: 10, currentStage: "ファイル検証中..." }));
      await new Promise(resolve => setTimeout(resolve, 500));

      setState(prev => ({ ...prev, progress: 30, currentStage: "アップロード中..." }));

      const formData = new FormData();
      formData.append("file", state.selectedFile);
      if (sessionId) {
        formData.append("session_id", sessionId);
      }

      // TODO: Get auth token from Firebase Auth
      const authToken = "dummy-token"; // This should come from Firebase Auth

      const response = await fetch("http://localhost:8000/api/v1/upload-image", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
        body: formData,
      });

      setState(prev => ({ ...prev, progress: 80, currentStage: "データ保存中..." }));

      const result = await response.json();

      if (response.ok && result.success) {
        setState(prev => ({ ...prev, progress: 100, currentStage: "完了", uploading: false }));
        onUploadSuccess(result.data);
      } else {
        throw new Error(result.error?.message || "アップロードに失敗しました");
      }
    } catch (error: any) {
      setState(prev => ({ ...prev, uploading: false, error: error.message }));
      onUploadError({
        code: "UPLOAD_FAILED",
        message: error.message,
      });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* File selection area */}
      <Paper
        variant="outlined"
        sx={{
          p: 4,
          textAlign: "center",
          cursor: disabled || state.uploading ? "default" : "pointer",
          backgroundColor: state.dragOver ? "action.hover" : "background.paper",
          borderStyle: state.dragOver ? "solid" : "dashed",
          borderColor: state.dragOver ? "primary.main" : "divider",
          borderWidth: 2,
          transition: "all 0.2s ease-in-out",
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          accept="image/jpeg,image/png"
          onChange={handleInputChange}
          disabled={disabled || state.uploading}
        />

        {!state.selectedFile ? (
          <Box>
            <CloudUploadIcon
              sx={{ fontSize: 48, color: "text.secondary", mb: 2 }}
            />
            <Typography variant="h6" gutterBottom>
              画像をアップロード
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ここにファイルをドラッグ&ドロップするか、クリックして選択
            </Typography>
            <Typography
              variant="caption"
              display="block"
              sx={{ mt: 0.5, color: "info.main" }}
            >
              注意: 顔写真以外の画像もアップロード可能です
            </Typography>
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              対応形式: JPEG, PNG（最大10MB）
            </Typography>
          </Box>
        ) : (
          <Box>
            {/* Preview display */}
            <img
              src={state.previewUrl || ""}
              alt="プレビュー"
              style={{
                maxWidth: "200px",
                maxHeight: "200px",
                objectFit: "contain",
                borderRadius: "8px",
              }}
            />
            <Typography variant="body2" sx={{ mt: 1 }}>
              {state.selectedFile.name} ({formatFileSize(state.selectedFile.size)})
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Upload progress */}
      {state.uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={state.progress} />
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            {state.currentStage} ({state.progress}%)
          </Typography>
        </Box>
      )}

      {/* Error display */}
      {state.error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {state.error}
        </Alert>
      )}

      {/* Action buttons */}
      <Box sx={{ mt: 2, display: "flex", gap: 2, justifyContent: "center" }}>
        {state.selectedFile && !state.uploading && (
          <>
            <Button variant="outlined" onClick={handleClear} disabled={disabled}>
              クリア
            </Button>
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={!state.selectedFile || state.uploading || disabled}
            >
              アップロード開始
            </Button>
          </>
        )}
      </Box>
    </Box>
  );
};

export default ImageUploader;
