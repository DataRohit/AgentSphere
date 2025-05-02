import { AgentsShowcase } from "@/components/agents-showcase";
import { FeaturesSection } from "@/components/features-section";
import { Footer } from "@/components/footer";
import { HeroSection } from "@/components/hero-section";
import { UseCasesSection } from "@/components/use-cases-section";

export default function Home() {
    return (
        <main className="min-h-screen">
            <HeroSection />
            <FeaturesSection />
            <AgentsShowcase />
            <UseCasesSection />
            <Footer />
        </main>
    );
}
