import { ThemeProvider, createTheme } from "@mui/material/styles";
import { Container, Box, Typography } from "@mui/material";
import QuestionnaireForm from "./components/QuestionnaireForm";

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
	return (
		<ThemeProvider theme={theme}>
			<Container
				sx={{
					mx: "auto",
				}}
			>
				<Typography
					variant="h4"
					component="h1"
					gutterBottom
					sx={{ mt: 4, fontWeight: "bold" }}
					textAlign="center"
				>
					このまま喫煙を続けると20年後の貴様はこうだ！！
				</Typography>

				<Box>
					<QuestionnaireForm />
				</Box>
			</Container>
		</ThemeProvider>
	);
}

export default App;
