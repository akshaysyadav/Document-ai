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
      color: "bg-primary",
      status: "MVP Ready",
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Analytics & Reports",
      description:
        "Comprehensive insights and performance metrics for data-driven decision making.",
      link: "/reports",
      color: "bg-primary",
    },
    {
      icon: <Monitor className="w-8 h-8" />,
      title: "Operations Dashboard",
      description:
        "Real-time monitoring and control center for the entire KMRL metro network.",
      link: "/dashboard",
      color: "bg-primary",
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-tr from-green-400/20 to-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-r from-purple-400/10 to-pink-600/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <Header />
      <main className="relative z-10">
        <HeroSection />

        {/* Features Overview Section */}
        <section className="py-24 relative">
          {/* Section background with gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-50/50 via-transparent to-purple-50/50 dark:from-blue-900/10 dark:via-transparent dark:to-purple-900/10"></div>
          
          <div className="container mx-auto px-6 relative z-10">
            <div className="text-center mb-20">
              <Badge className="mb-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0 px-6 py-2 text-sm font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                ✨ Platform Overview
              </Badge>
              <h2 className="text-5xl font-display font-bold mb-8 bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 bg-clip-text text-transparent leading-tight">
                Comprehensive Metro Management Platform
              </h2>
              <p className="text-xl text-muted-foreground max-w-4xl mx-auto leading-relaxed">
                Experience the future of metro operations with our integrated
                AI-powered platform. From intelligent scheduling to document
                automation, everything you need in one place.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-6xl mx-auto">
              {features.slice(0, 2).map((feature, index) => (
                <Card
                  key={index}
                  className="group relative overflow-hidden backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border-0 shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] hover:-translate-y-2"
                >
                  {/* Card glow effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  
                  <CardContent className="p-10 relative z-10">
                    <div className="flex items-center justify-between mb-8">
                      <div
                        className={`w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 shadow-lg`}
                      >
                        {feature.icon}
                      </div>
                      {feature.status && (
                        <Badge className="bg-gradient-to-r from-green-500 to-emerald-500 text-white border-0 px-4 py-2 shadow-lg animate-pulse">
                          <Rocket className="w-4 h-4 mr-2" />
                          {feature.status}
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-3xl mb-6 text-foreground group-hover:text-blue-600 transition-colors duration-300 font-bold">
                      {feature.title}
                    </CardTitle>
                    <CardDescription className="text-muted-foreground mb-8 text-lg leading-relaxed">
                      {feature.description}
                    </CardDescription>
                    <Link to={feature.link}>
                      <Button
                        variant="outline"
                        className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-700 hover:bg-gradient-to-r hover:from-blue-600 hover:to-purple-600 hover:text-white hover:border-transparent transition-all duration-300 group-hover:shadow-lg hover:scale-105"
                      >
                        Explore Platform
                        <ArrowRight className="w-5 h-5 ml-3 group-hover:translate-x-2 transition-transform duration-300" />
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Third card centered below the first two */}
            <div className="flex justify-center mt-12 max-w-6xl mx-auto">
              <div className="w-full md:w-1/2">
                <Card className="group relative overflow-hidden backdrop-blur-sm bg-white/80 dark:bg-slate-800/80 border-0 shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] hover:-translate-y-2">
                  {/* Card glow effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  
                  <CardContent className="p-10 relative z-10">
                    <div className="flex items-center justify-between mb-8">
                      <div
                        className={`w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 shadow-lg`}
                      >
                        {features[2].icon}
                      </div>
                      {features[2].status && (
                        <Badge className="bg-gradient-to-r from-green-500 to-emerald-500 text-white border-0 px-4 py-2 shadow-lg animate-pulse">
                          <Rocket className="w-4 h-4 mr-2" />
                          {features[2].status}
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-3xl mb-6 text-foreground group-hover:text-blue-600 transition-colors duration-300 font-bold">
                      {features[2].title}
                    </CardTitle>
                    <CardDescription className="text-muted-foreground mb-8 text-lg leading-relaxed">
                      {features[2].description}
                    </CardDescription>
                    <Link to={features[2].link}>
                      <Button
                        variant="outline"
                        className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-700 hover:bg-gradient-to-r hover:from-blue-600 hover:to-purple-600 hover:text-white hover:border-transparent transition-all duration-300 group-hover:shadow-lg hover:scale-105"
                      >
                        Explore Platform
                        <ArrowRight className="w-5 h-5 ml-3 group-hover:translate-x-2 transition-transform duration-300" />
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Stats Section */}
        <section className="py-24 relative">
          <div className="container mx-auto px-6 relative z-10">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-display font-bold mb-6 text-foreground">
                Live Metro Operations
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Real-time statistics from the KMRL network
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-6xl mx-auto">
              {stats.map((stat, index) => (
                <Card key={index} className="group relative overflow-hidden bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm border-0 shadow-2xl hover:shadow-3xl transition-all duration-500 hover:scale-110 hover:-translate-y-3">
                  {/* Card inner glow */}
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-purple-600/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  
                  <CardContent className="p-8 text-center relative z-10">
                    <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 text-white mx-auto mb-6 group-hover:scale-110 group-hover:rotate-12 transition-all duration-500 shadow-lg">
                      {stat.icon}
                    </div>
                    <div className="text-4xl font-bold text-foreground mb-3 group-hover:text-blue-600 transition-colors duration-300">
                      {stat.value}
                    </div>
                    <div className="text-muted-foreground font-medium text-lg">
                      {stat.label}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="text-center mt-16">
              <Link to="/dashboard">
                <Button size="lg" className="h-14 px-8 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 shadow-lg">
                  View Full Dashboard
                  <ArrowRight className="w-5 h-5 ml-3" />
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
