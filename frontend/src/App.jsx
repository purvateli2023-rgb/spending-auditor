import { useState } from "react"
import Upload from "./components/Upload"
import Dashboard from "./components/Dashboard"
import SplashCursor from "./components/SplashCursor"

function App() {
  const [transactions, setTransactions] = useState(null)

  return (
    <div className="app">
      <SplashCursor />
      {transactions === null ? (
        <Upload onSuccess={setTransactions} />
      ) : (
        <Dashboard
          transactions={transactions}
          onReset={() => setTransactions(null)}
        />
      )}
    </div>
  )
}

export default App