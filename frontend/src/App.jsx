import SQLChat from './components/SQLChat'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Background pattern */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-700/10 via-transparent to-transparent pointer-events-none" />
      
      {/* Main content */}
      <div className="relative z-10">
        <SQLChat />
      </div>
    </div>
  )
}

export default App
