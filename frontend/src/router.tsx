import { createBrowserRouter, Navigate } from "react-router-dom";
import Splash from "./pages/Splash";
import Chat from "./pages/Chat";

export const router = createBrowserRouter([
  { path: "/", element: <Splash /> },
  { path: "/chat", element: <Chat /> },
  { path: "*", element: <Navigate to="/" replace /> },
]);
