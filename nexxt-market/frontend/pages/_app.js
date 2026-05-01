import '../styles/globals.css'
import { Toaster } from 'react-hot-toast'

export default function App({ Component, pageProps }) {
  return (
    <>
      <div className="noise-bg" />
      <Component {...pageProps} />
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#1a1a1a',
            color: '#f0f0f0',
            border: '1px solid #2a2a2a',
            fontFamily: 'DM Sans, sans-serif',
          },
        }}
      />
    </>
  )
}
