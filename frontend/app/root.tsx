import { Outlet } from "react-router"
import appStylesHref from "./app.css?url"

export default function App() {
  return (
    <html>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="stylesheet" href={appStylesHref} />
        <title>Jobify</title>
      </head>
      <body>
        <Outlet></Outlet>
      </body>
    </html>
  );
}

