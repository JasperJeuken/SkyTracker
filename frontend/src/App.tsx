import { useState } from 'react'
import './App.css';
import { AircraftMap } from './components/AircraftMap';
import { Layout } from './components/layout/Layout';
import { ThemeProvider } from './components/layout/ThemeProvider';


function App() {

  return (
    <ThemeProvider>
      <Layout>
        {(props: { mapStyle: "Default" | "Satellite"}) => (
          <AircraftMap mapStyle={props.mapStyle} />
        )}
      </Layout>
    </ThemeProvider>
  );
}

export default App
