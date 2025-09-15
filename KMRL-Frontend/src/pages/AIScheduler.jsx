import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, Clock, Train, Settings, BarChart3, AlertTriangle, CheckCircle, Zap } from "lucide-react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const AIScheduler = () => {
  const scheduleData = [
    { 
      id: "TR001", 
      route: "Aluva ↔ Pettah", 
      departure: "06:00", 
      arrival: "06:45", 
      status: "On Time", 
      efficiency: 98,
      type: "Express"
    },
    { 
      id: "TR002", 
      route: "Aluva ↔ Maharaja's", 
      departure: "06:15", 
      arrival: "07:05", 
      status: "Delayed", 
      efficiency: 85,
      type: "Regular"
    },
    { 
      id: "TR003", 
      route: "Palarivattom ↔ Pettah", 
      departure: "06:30", 
      arrival: "07:00", 
      status: "On Time", 
      efficiency: 95,
      type: "Express"
    },
    { 
      id: "TR004", 
      route: "Edapally ↔ MG Road", 
      departure: "06:45", 
      arrival: "07:20", 
      status: "Early", 
      efficiency: 102,
      type: "Regular"
    }
  ];

  const aiFeatures = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time Optimization",
      description: "AI continuously adjusts schedules based on passenger flow, weather conditions, and maintenance needs."
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Predictive Analytics",
      description: "Forecast demand patterns and optimize train frequency to reduce wait times and overcrowding."
    },
    {
      icon: <Settings className="w-6 h-6" />,
      title: "Smart Maintenance Scheduling",
      description: "Automatically schedule maintenance windows to minimize service disruptions."
    },
    {
      icon: <AlertTriangle className="w-6 h-6" />,
      title: "Incident Management",
      description: "Instantly reroute trains and notify passengers during service disruptions."
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="pt-20">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-primary to-secondary text-white py-20">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto text-center">
              <Badge className="mb-6 bg-white/20 text-white border-white/30">
                Metro Scheduling
              </Badge>
              <h1 className="text-5xl font-display font-bold mb-6">
                Intelligent Metro Train Scheduling
              </h1>
              <p className="text-xl mb-8 text-white/90">
                Advanced AI algorithms optimize train schedules in real-time, ensuring maximum efficiency 
                and passenger satisfaction across the entire KMRL network.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" variant="secondary" className="font-semibold">
                  <Calendar className="w-5 h-5 mr-2" />
                  View Live Schedule
                </Button>
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary">
                  <Settings className="w-5 h-5 mr-2" />
                  Optimization Settings
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* AI Features Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-display font-bold mb-4 text-foreground">
                AI-Powered Features
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Our advanced AI system revolutionizes metro operations with intelligent automation
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {aiFeatures.map((feature, index) => (
                <Card key={index} className="hover-lift">
                  <CardHeader>
                    <div className="flex items-center gap-4">
                      <div className="p-3 rounded-lg bg-primary/10 text-primary">
                        {feature.icon}
                      </div>
                      <CardTitle className="text-xl">{feature.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Live Schedule Dashboard */}
        <section className="py-20">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-display font-bold mb-4 text-foreground">
                Live Schedule Dashboard
              </h2>
              <p className="text-xl text-muted-foreground">
                Real-time monitoring of all metro train schedules
              </p>
            </div>

            <Card className="shadow-strong">
              <CardHeader className="bg-gradient-to-r from-primary/5 to-secondary/5">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl text-foreground">Metro Schedule Control</CardTitle>
                    <CardDescription>AI-optimized train scheduling system</CardDescription>
                  </div>
                  <Button className="gradient-hero text-white">
                    <Zap className="w-4 h-4 mr-2" />
                    Run AI Optimization
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-b border-border">
                      <tr className="bg-muted/30">
                        <th className="text-left p-4 font-semibold">Train ID</th>
                        <th className="text-left p-4 font-semibold">Route</th>
                        <th className="text-left p-4 font-semibold">Departure</th>
                        <th className="text-left p-4 font-semibold">Arrival</th>
                        <th className="text-left p-4 font-semibold">Status</th>
                        <th className="text-left p-4 font-semibold">Efficiency</th>
                        <th className="text-left p-4 font-semibold">Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scheduleData.map((train) => (
                        <tr key={train.id} className="border-b border-border/50 hover:bg-muted/20">
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <Train className="w-4 h-4 text-primary" />
                              <span className="font-medium">{train.id}</span>
                            </div>
                          </td>
                          <td className="p-4 text-muted-foreground">{train.route}</td>
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-muted-foreground" />
                              {train.departure}
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-muted-foreground" />
                              {train.arrival}
                            </div>
                          </td>
                          <td className="p-4">
                            <Badge 
                              variant={
                                train.status === "On Time" ? "default" : 
                                train.status === "Early" ? "secondary" : 
                                "destructive"
                              }
                            >
                              {train.status === "On Time" && <CheckCircle className="w-3 h-3 mr-1" />}
                              {train.status === "Early" && <CheckCircle className="w-3 h-3 mr-1" />}
                              {train.status === "Delayed" && <AlertTriangle className="w-3 h-3 mr-1" />}
                              {train.status}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <div className="w-12 h-2 bg-secondary/20 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-secondary rounded-full transition-smooth"
                                  style={{ width: `${Math.min(train.efficiency, 100)}%` }}
                                />
                              </div>
                              <span className="text-sm font-medium">{train.efficiency}%</span>
                            </div>
                          </td>
                          <td className="p-4">
                            <Badge variant="outline">
                              {train.type}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default AIScheduler;