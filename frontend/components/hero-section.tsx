import { Navbar } from "@/components/navbar";
import { Button } from "@/components/ui/button";
import { ArrowRight, Search } from "lucide-react";

export function HeroSection() {
    return (
        <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
            <Navbar />
            <div className="absolute inset-0 -z-10 bg-grid-pattern opacity-[0.02] dark:opacity-[0.05]" />
            <div className="container flex flex-col items-center text-center z-10 px-4 md:px-6">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter mb-4">
                    AgentSphere
                </h1>
                <p className="text-xl md:text-2xl text-(--muted-foreground) max-w-[800px] mb-8">
                    A dynamic AI platform enabling one-on-one and group interactions with
                    specialized AI agents
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                    <Button
                        size="lg"
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:scale-105 hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-8 w-40 h-12 cursor-pointer"
                    >
                        <span className="relative z-10 flex items-center">
                            Get Started
                            <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-300" />
                        </span>
                        <span className="absolute inset-0 bg-(--primary-foreground)/80 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                    <Button
                        size="lg"
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:scale-105 hover:shadow-lg border border-(--secondary) bg-(--secondary) text-(--secondary-foreground) dark:bg-(--secondary) dark:text-(--secondary-foreground) dark:border-(--secondary) px-8 w-40 h-12 cursor-pointer"
                    >
                        <span className="relative z-10 flex items-center">
                            Explore{" "}
                            <Search className="ml-2 h-4 w-4 transition-transform duration-300" />
                        </span>
                        <span className="absolute inset-0 bg-(--secondary-foreground)/10 dark:bg-(--secondary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-right"></span>
                    </Button>
                </div>
            </div>
            <div className="absolute inset-0 -z-20">
                <div className="absolute inset-0 bg-grid-small-pattern opacity-[0.15] dark:opacity-[0.05]" />
            </div>
        </section>
    );
}
