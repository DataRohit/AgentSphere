import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UserIcon, UsersIcon } from "lucide-react";

export function UseCasesSection() {
    return (
        <section id="use-cases" className="py-20 md:py-28 bg-(--muted/50 dark:bg-(--muted)/10">
            <div className="container mx-auto px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold tracking-tighter mb-4">
                        Use Cases
                    </h2>
                    <p className="text-(--muted-foreground) max-w-[700px] mx-auto">
                        Discover how AgentSphere can enhance your productivity and streamline your
                        workflows
                    </p>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-16">
                    <Card className="border bg-(--background) gap-0 justify-center">
                        <CardHeader>
                            <div className="flex items-center space-x-4 mb-2">
                                <div className="p-2 rounded-full bg-(--primary)/10">
                                    <UserIcon className="h-6 w-6 text-(--primary)" />
                                </div>
                                <CardTitle>One-on-One Chat</CardTitle>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <p className="text-(--muted-foreground)">
                                Direct conversations with specialized AI agents for focused
                                assistance and information retrieval.
                            </p>
                            <ul className="space-y-2">
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Personal assistance for specific tasks
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Detailed information from specialized agents
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Message history tracking and editing
                                    </span>
                                </li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card className="border bg-(--background) gap-0">
                        <CardHeader>
                            <div className="flex items-center space-x-4 mb-2">
                                <div className="p-2 rounded-full bg-(--primary)/10">
                                    <UsersIcon className="h-6 w-6 text-(--primary)" />
                                </div>
                                <CardTitle>Group Chat</CardTitle>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <p className="text-(--muted-foreground)">
                                Multi-agent conversations where different specialized agents
                                collaborate to solve complex problems.
                            </p>
                            <ul className="space-y-2">
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Collaborative problem-solving with multiple agents
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Automated routing to appropriate agents
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Complex workflows with multiple steps
                                    </span>
                                </li>
                            </ul>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </section>
    );
}
