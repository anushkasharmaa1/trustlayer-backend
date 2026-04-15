  import { useState, useEffect } from "react";

export default function Dashboard() {

const [data,setData] = useState(null)
const [loading,setLoading] = useState(true)

useEffect(()=>{

fetch("http://127.0.0.1:8000/report?user_id=gig_worker_001")
.then(res=>res.json())
.then(d=>{
setData(d)
setLoading(false)
})

},[])

if(loading) return <div style={{padding:40}}>Loading Dashboard...</div>

const signals = data.signals || {}

return(

<div style={{display:"flex",height:"100vh",fontFamily:"sans-serif"}}>

{/* SIDEBAR */}

<div style={{
width:220,
background:"#F7F9FB",
borderRight:"1px solid #e5e7eb",
padding:20
}}>

<h3>TrustLayer</h3>

<div style={{marginTop:30}}>

<p>Dashboard</p>
<p>Signals</p>
<p>Simulator</p>
<p>Factors</p>

</div>

</div>

{/* MAIN */}

<div style={{flex:1,padding:30,background:"#F1F5F9"}}>

{/* TOP CARDS */}

<div style={{
display:"grid",
gridTemplateColumns:"repeat(4,1fr)",
gap:20,
marginBottom:30
}}>

<Card title="Trust Score" value={data.trust_score}/>
<Card title="Monthly Income" value={`₹${data.income}`}/>
<Card title="Savings Rate" value={`${Math.round(data.savings_rate*100)}%`}/>
<Card title="Bill Regularity" value={`${Math.round(data.bill_regularity*100)}%`}/>

</div>

{/* CHART AREA */}

<div style={{
display:"grid",
gridTemplateColumns:"2fr 1fr",
gap:20
}}>

{/* SIGNAL BARS */}

<div style={{
background:"white",
padding:20,
borderRadius:10
}}>

<h3>Behavior Signals</h3>

{Object.entries(signals).map(([k,v])=>(

<div key={k} style={{marginBottom:10}}>

<div style={{
display:"flex",
justifyContent:"space-between"
}}>

<span>{k}</span>
<span>{Math.round(v*100)}%</span>

</div>

<div style={{
height:6,
background:"#e5e7eb",
borderRadius:4
}}>

<div style={{
height:"100%",
width:`${v*100}%`,
background:"#4F46E5",
borderRadius:4
}}/>

</div>

</div>

))}

</div>

{/* SCORE PANEL */}

<div style={{
background:"white",
padding:20,
borderRadius:10
}}>

<h3>Credit Summary</h3>

<p style={{fontSize:40,fontWeight:"bold"}}>
{data.trust_score}
</p>

<p>Financial Behavior Score</p>

</div>

</div>

</div>

</div>

)

}

function Card({title,value}){

return(

<div style={{
background:"white",
padding:20,
borderRadius:10
}}>

<p style={{color:"#64748B"}}>{title}</p>

<h2>{value}</h2>

</div>

)

}