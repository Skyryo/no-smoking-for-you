import { ThemeProvider, createTheme } from "@mui/material/styles";
import { Container, Box, Typography } from "@mui/material";
import QuestionnaireForm from "./components/QuestionnaireForm";
import IconImage from "../no_smoking_for_you.svg";

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
				<img
					width={100}
					src={IconImage}
					alt="Description"
					style={{ display: "block", margin: "0 auto 0 auto" }}
				/>
				<Typography
					variant="h5"
					component="h1"
					gutterBottom
					sx={{ mt: 2, fontWeight: "bold" }}
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
