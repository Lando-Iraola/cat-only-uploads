import Image from "next/image";

type Cats = {
    img_name: string;
    img_src: string;
}

async function getCats(): Promise<Cats[]>{
    const res = await fetch("http://localhost:8000/cats", 
    { cache:"no-store"});

    return res.json()
}

export default async function Home() {
  const cats = await getCats();
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
	<ul>
	 {
	     cats.map((cat) => (<li key={cat.img_name}> <img src={cat.img_src}/>   </li>))
	 }
	</ul>
     </main>
    </div>
  );
}
