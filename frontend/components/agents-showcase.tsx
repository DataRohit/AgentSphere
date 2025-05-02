import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CloudIcon, MagnifyingGlassIcon, NewspaperIcon } from "@heroicons/react/24/outline";

const agents = [
    {
        name: "News Agent",
        description: "Stay updated with the latest news & headlines from various sources.",
        icon: NewspaperIcon,
        tags: ["News", "Headlines", "Updates"],
    },
    {
        name: "Weather Agent",
        description: "Get real-time weather forecasts and alerts for any location worldwide",
        icon: CloudIcon,
        tags: ["Weather", "Forecast", "Alerts"],
    },
    {
        name: "SerpAPI Google Agent",
        description: "Search the web and retrieve information from Google search results",
        icon: MagnifyingGlassIcon,
        tags: ["Search", "Web", "Information"],
    },
];

export function AgentsShowcase() {
    return (
        <section id="agents" className="py-20 md:py-28">
            <div className="container mx-auto px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold tracking-tighter mb-4">
                        Specialized Agents
                    </h2>
                    <p className="text-(--muted-foreground) max-w-[700px] mx-auto">
                        Interact with purpose-built AI agents designed to handle specific tasks and
                        provide valuable information
                    </p>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                    {agents.map((agent, index) => (
                        <Card
                            key={index}
                            className="border bg-(--background) overflow-hidden transition-all hover:shadow-md"
                        >
                            <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                    <agent.icon className="h-8 w-8 text-(--primary)" />
                                    <div className="h-10 w-10 rounded-full bg-(--muted) flex items-center justify-center">
                                        <span className="text-xs font-medium">AI</span>
                                    </div>
                                </div>
                                <CardTitle className="text-xl mt-4">{agent.name}</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <p className="text-(--muted-foreground) text-sm">
                                    {agent.description}
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {agent.tags.map((tag, tagIndex) => (
                                        <Badge key={tagIndex} variant="secondary">
                                            {tag}
                                        </Badge>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        </section>
    );
}
