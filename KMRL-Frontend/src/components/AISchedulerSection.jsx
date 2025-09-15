import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Bus, 
  Fuel, 
  ShieldCheck, 
  Sparkles, 
  Clock, 
  Calendar,
  ArrowRight,
  TrendingUp
} from "lucide-react";

const AISchedulerSection = () => {
  const optimizationFeatures = [
    {
      icon: Bus,
      title: "Train Availability",
      description: "Real-time metro fleet management and availability tracking"
    },
    {
      icon: Fuel,
      title: "Energy Optimization",
      description: "Intelligent route planning to minimize energy consumption"
    },
    {
      icon: ShieldCheck,
      title: "Safety Protocols",
      description: "Automated safety checks and compliance monitoring"
    },
    {
      icon: Sparkles,
      title: "Smart Maintenance",
      description: "Optimized maintenance and cleaning schedules"
    },
    {
      icon: Clock,
      title: "Time Efficiency",
      description: "AI-driven scheduling to maximize operational efficiency"
    }
  ];

  const scheduleData = [
    { route: "Blue Line", departure: "06:00 AM", arrival: "07:30 AM", status: "On Time", efficiency: "98%" },
    { route: "Green Line", departure: "06:15 AM", arrival: "08:00 AM", status: "On Time", efficiency: "95%" },
    { route: "Red Line", departure: "06:30 AM", arrival: "08:15 AM", status: "Optimized", efficiency: "100%" },
    { route: "Purple Line", departure: "06:45 AM", arrival: "08:30 AM", status: "On Time", efficiency: "97%" }
  ];

  return (
    <section id="scheduler" className="py-20 bg-muted/30">
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-primary/10 text-primary border-primary/20">
            AI-Powered Optimization
          </Badge>
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Intelligent <span className="gradient-text-hero">Metro Scheduling</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our AI analyzes multiple factors to create optimal schedules that improve efficiency, reduce costs, and enhance passenger experience.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Features Grid */}
          <div>
            <h3 className="text-2xl font-display font-bold mb-8">Optimization Factors</h3>
            <div className="grid sm:grid-cols-2 gap-6">
              {optimizationFeatures.map((feature, index) => (
                <Card 
                  key={index} 
                  className="hover-lift gradient-card border-0 shadow-soft"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <CardContent className="p-6">
                    <feature.icon className="w-8 h-8 text-primary mb-4" />
                    <h4 className="font-semibold mb-2">{feature.title}</h4>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Schedule Dashboard Mockup */}
          <div>
            <Card className="shadow-strong border-0 overflow-hidden">
              <CardHeader className="gradient-hero text-white">
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  AI Schedule Dashboard
                </CardTitle>
                <p className="text-white/80 text-sm">Today's Optimized Routes</p>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-border">
                  {scheduleData.map((schedule, index) => (
                    <div key={index} className="p-4 hover:bg-muted/50 transition-smooth">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold">{schedule.route}</div>
                          <div className="text-sm text-muted-foreground">
                            {schedule.departure} → {schedule.arrival}
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge 
                            variant={schedule.status === "Optimized" ? "default" : "secondary"}
                            className={schedule.status === "Optimized" ? "bg-secondary text-white" : ""}
                          >
                            {schedule.status}
                          </Badge>
                          <div className="text-sm text-muted-foreground mt-1">
                            <TrendingUp className="w-3 h-3 inline mr-1" />
                            {schedule.efficiency}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-4 bg-muted/30 text-center">
                  <Button className="w-full gradient-hero text-white border-0 hover:opacity-90">
                    <span className="text-primary-foreground">Run AI Scheduling</span>
                    <ArrowRight className="ml-2 w-4 h-4 text-primary-foreground" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AISchedulerSection;