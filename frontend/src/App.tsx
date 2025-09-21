import './App.css';
import { Layout } from './components/layout/Layout';
import { ThemeProvider } from './components/layout/ThemeProvider';


function App() {

  return (
    <ThemeProvider>
      <Layout />
    </ThemeProvider>
  );
}

export default App
