import { useEffect, useState } from 'react'

import './App.css'

function App() {
  const urlParams = new URLSearchParams(window.location.search);
  const [jobBoard, setJobBoard] = useState([])

  const fetchCompanyJobBoard = async (companyName : string) => {
    const response = await fetch(`/api/job-boards/${companyName}`)
    const result = await response.json();
    setJobBoard(result)
  }

  useEffect(() => {
    const company = urlParams.get("company")
    if (!company) {
      return
    }
    fetchCompanyJobBoard(company)
  }, [])

  return (
    <>
      {jobBoard.map((job: any) => 
        <div>
          <h2>{job.title}</h2>
          <p>{job.description}</p>
        </div>
)}
    </>
  )
}

export default App
