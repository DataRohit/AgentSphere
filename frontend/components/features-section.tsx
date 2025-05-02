import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    ChatBubbleLeftRightIcon,
    CogIcon,
    LockClosedIcon,
    UserGroupIcon,
} from "@heroicons/react/24/outline";

const features = [
    {
        title: "AI Agents",
        description: "Create and manage AI agents with customizable system prompts.",
        icon: ChatBubbleLeftRightIcon,
    },
    {
        title: "Multi-User",
        description: "Collaborative environment with organizations and members",
        icon: UserGroupIcon,
    },
    {
        title: "MCP Tools",
        description: "Integrate external tools via MCP servers for task automation",
        icon: CogIcon,
    },
    {
        title: "Secure",
        description: "API keys stored securely in HashiCorp Vault for authentication",
        icon: LockClosedIcon,
    },
];

export function FeaturesSection() {
    return (
        <section id="features" className="py-20 md:py-28 bg-muted/50 dark:bg-muted/10">
            <div className="container mx-auto px-4 md:px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold tracking-tighter mb-4">
                        Key Features
                    </h2>
                    <p className="text-(--muted-foreground) max-w-[700px] mx-auto">
                        AgentSphere provides powerful tools for AI agent interactions and workflow
                        automation
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-4 gap-6">
                    {features.map((feature, index) => (
                        <Card key={index} className="border bg-(--background) gap-0">
                            <CardHeader className="pb-2">
                                <feature.icon className="h-10 w-10 mb-4 text-(--primary)" />
                                <CardTitle className="text-xl">{feature.title}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-(--muted-foreground) text-sm">
                                    {feature.description}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <div className="mt-16 grid grid-cols-1 2xl:grid-cols-3 gap-8">
                    <Card className="border bg-(--background) gap-0">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-xl">Organization Management</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-2">
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Create up to 3 organizations per user
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Add up to 8 members per organization
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Manage resource visibility (public/private)
                                    </span>
                                </li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card className="border bg-(--background) gap-0">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-xl">Agent Creation</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-2">
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Create up to 5 agents per user per organization
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Customize system prompts and behaviors
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Auto-generated avatars using DiceBear
                                    </span>
                                </li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card className="border bg-(--background) gap-0">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-xl">MCP Tool Integration</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-2">
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Add up to 5 MCP tools per organization
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Define tools by name, description, URL, and tags
                                    </span>
                                </li>
                                <li className="flex items-start">
                                    <span className="mr-2">•</span>
                                    <span className="text-sm text-(--muted-foreground)">
                                        Secure authentication with external services
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
