import { Github, Linkedin } from "lucide-react";
import Link from "next/link";

export function Footer() {
    return (
        <footer className="border-t py-12 md:py-16">
            <div className="container px-4 md:px-6 mx-auto max-w-screen-xl">
                <div className="flex flex-col space-y-4 md:space-y-0 md:flex-row justify-between items-center">
                    <div className="mb-6 md:mb-0">
                        <div className="flex items-center space-x-2 w-36 group cursor-pointer">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="h-5 w-5 transition-transform duration-700 ease-in-out group-hover:rotate-[360deg]"
                            >
                                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                                <polyline points="3.29 7 12 12 20.71 7" />
                                <line x1="12" y1="22" x2="12" y2="12" />
                            </svg>
                            <span className="font-medium">AgentSphere</span>
                        </div>
                    </div>
                    <div className="flex flex-col items-center gap-2">
                        <p className="text-(--muted-foreground)">
                            Created by Rohit Ingole / DataRohit
                        </p>
                    </div>
                    <div className="flex md:space-x-4 w-20 md:w-36 mt-2 md:mt-0 justify-around md:justify-end">
                        <Link
                            href="https://github.com/DataRohit/AgentSphere"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-(--muted-foreground) hover:text-(--foreground) transition-all duration-300 hover:scale-110"
                        >
                            <Github className="h-5 w-5 transition-transform duration-300 hover:rotate-[20deg]" />
                            <span className="sr-only">GitHub</span>
                        </Link>
                        <Link
                            href="https://www.linkedin.com/in/rohit-vilas-ingole/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-(--muted-foreground) hover:text-(--foreground) transition-all duration-300 hover:scale-110"
                        >
                            <Linkedin className="h-5 w-5 transition-transform duration-300 hover:rotate-[20deg]" />
                            <span className="sr-only">LinkedIn</span>
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
