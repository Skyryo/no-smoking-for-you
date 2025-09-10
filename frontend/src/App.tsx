import { ThemeProvider, createTheme } from "@mui/material/styles";
import { CssBaseline, Container, Typography, Box } from "@mui/material";
import ImageUploader from "./components/ImageUploader";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
  },
});

function App() {
  const handleUploadSuccess = (result: any) => {
    console.log("Upload successful:", result);
    // TODO: Navigate to next step or show success message
  };

  const handleUploadError = (error: any) => {
    console.error("Upload error:", error);
    // Error is already handled in the component
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            No Smoking for You
          </Typography>
          <Typography variant="h6" color="text.secondary" align="center" sx={{ mb: 4 }}>
            画像をアップロードしてください
          </Typography>
          
          <ImageUploader
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
