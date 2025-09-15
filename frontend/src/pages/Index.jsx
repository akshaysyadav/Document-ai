import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Train,
  FileText,
  BarChart3,
  Monitor,
  ArrowRight,
  Zap,
  CheckCircle,
  Rocket,
} from "lucide-react";
import { Link } from "react-router-dom";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import AboutSection from "@/components/AboutSection";
import Footer from "@/components/Footer";

const Index = () => {
  const features = [
    // Removed AI Scheduler for MVP
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Document Intelligence MVP",
      description:
        "🚀 AI-powered document processing with OCR, NLP, and vector search capabilities - MVP Ready!",
      link: "/documents",
      color: "from-secondary to-secondary-light",
      status: "MVP Ready",
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Analytics & Reports",
      description:
        "Comprehensive insights and performance metrics for data-driven decision making.",
      link: "/reports",
      color: "from-primary to-secondary",
    },
    {
      icon: <Monitor className="w-8 h-8" />,
      title: "Operations Dashboard",
      description:
        "Real-time monitoring and control center for the entire KMRL metro network.",
      link: "/dashboard",
      color: "from-secondary to-primary",
    },
  ];

  const stats = [
    {
      value: "28",
      label: "Active Trains",
      icon: <Train className="w-5 h-5" />,
    },
    {
      value: "187K",
      label: "Daily Passengers",
      icon: <CheckCircle className="w-5 h-5" />,
    },
    {
      value: "94.7%",
      label: "On-Time Performance",
      icon: <Zap className="w-5 h-5" />,
    },
    {
      value: "25",
      label: "Metro Stations",
      icon: <Monitor className="w-5 h-5" />,
    },
  ];

  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <HeroSection />

        {/* Features Overview Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <Badge className="mb-4 bg-primary/10 text-primary border-primary/20">
                Platform Overview
              </Badge>
              <h2 className="text-4xl font-display font-bold mb-6 text-foreground">
                Comprehensive Metro Management Platform
              </h2>
              <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
                Experience the future of metro operations with our integrated
                AI-powered platform. From intelligent scheduling to document
                automation, everything you need in one place.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
              {features.map((feature, index) => (
                <Card
                  key={index}
                  className="hover-lift group border-2 hover:border-primary/30 transition-all duration-300"
                >
                  <CardContent className="p-8">
                    <div className="flex items-center justify-between mb-6">
                      <div
                        className={`w-16 h-16 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center text-white group-hover:scale-110 transition-transform duration-300`}
                      >
                        {feature.icon}
                      </div>
                      {feature.status && (
                        <Badge className="bg-green-100 text-green-700 border-green-200">
                          <Rocket className="w-3 h-3 mr-1" />
                          {feature.status}
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-2xl mb-4 text-foreground group-hover:text-primary transition-colors">
                      {feature.title}
                    </CardTitle>
                    <CardDescription className="text-muted-foreground mb-6 text-base leading-relaxed">
                      {feature.description}
                    </CardDescription>
                    <Link to={feature.link}>
                      <Button
                        variant="outline"
                        className="w-full group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-all duration-300"
                      >
                        Explore
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Quick Stats Section */}
        <section className="py-20">
          <div className="container mx-auto px-6">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-display font-bold mb-4 text-foreground">
                Live Metro Operations
              </h2>
              <p className="text-lg text-muted-foreground">
                Real-time statistics from the KMRL network
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {stats.map((stat, index) => (
                <Card key={index} className="text-center hover-lift">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 text-primary mx-auto mb-4">
                      {stat.icon}
                    </div>
                    <div className="text-3xl font-bold text-foreground mb-2">
                      {stat.value}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {stat.label}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="text-center mt-12">
              <Link to="/dashboard">
                <Button size="lg" className="gradient-hero text-white">
                  <Monitor className="w-5 h-5 mr-2" />
                  View Live Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <AboutSection />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
