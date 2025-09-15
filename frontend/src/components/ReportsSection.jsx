import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Target,
  Download,
  ArrowRight,
  PieChart,
  Activity
} from "lucide-react";

const ReportsSection = () => {
  const insights = [
    {
      title: "Operational Efficiency",
      value: "94.2%",
      change: "+12.5%",
      trend: "up",
      icon: Target
    },
    {
      title: "Time Saved Daily",
      value: "8.5 hrs",
      change: "+3.2 hrs",
      trend: "up",
      icon: Clock
    },
    {
      title: "Cost Reduction",
      value: "₹2.4L",
      change: "+₹45K",
      trend: "up",
      icon: TrendingUp
    },
    {
      title: "Fleet Utilization",
      value: "87.6%",
      change: "+5.8%",
      trend: "up",
      icon: Activity
    }
  ];

  const chartData = [
    { month: "Jan", efficiency: 78, utilization: 82 },
    { month: "Feb", efficiency: 82, utilization: 85 },
    { month: "Mar", efficiency: 85, utilization: 88 },
    { month: "Apr", efficiency: 89, utilization: 90 },
    { month: "May", efficiency: 92, utilization: 92 },
    { month: "Jun", efficiency: 94, utilization: 88 }
  ];

  return (
    <section id="reports" className="py-20 bg-muted/30">
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-primary/10 text-primary border-primary/20">
            Data-Driven Insights
          </Badge>
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Real-Time <span className="gradient-text-hero">Reports & Analytics</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Monitor performance, track efficiency gains, and make data-driven decisions with comprehensive analytics and reporting.
          </p>
        </div>

        {/* Insights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {insights.map((insight, index) => (
            <Card 
              key={index} 
              className="hover-lift gradient-card border-0 shadow-soft text-center text-primary-foreground"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardContent className="p-6">
                <insight.icon className="w-8 h-8 text-primary mx-auto mb-4" />
                <div className="text-3xl font-bold gradient-text-hero mb-2">
                  {insight.value}
                </div>
                <div className="text-sm font-medium mb-2">{insight.title}</div>
                <div className="flex items-center justify-center gap-1 text-xs">
                  <TrendingUp className="w-3 h-3 text-secondary" />
                  <span className="text-secondary">{insight.change}</span>
                  <span className="text-muted-foreground">this month</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-16">
          {/* Chart Visualization */}
          <Card className="shadow-strong border-0">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                Performance Trends
              </CardTitle>
              <p className="text-muted-foreground text-sm">Monthly efficiency and utilization rates</p>
            </CardHeader>
            <CardContent>
              {/* Simplified Chart Visualization */}
              <div className="space-y-4">
                {chartData.map((data, index) => (
                  <div key={index} className="flex items-center gap-4">
                    <div className="w-8 text-sm font-medium">{data.month}</div>
                    <div className="flex-1 flex gap-2">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-muted-foreground">Efficiency</span>
                          <span className="text-xs font-medium">{data.efficiency}%</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary rounded-full transition-all duration-1000"
                            style={{ width: `${data.efficiency}%` }}
                          />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-muted-foreground">Utilization</span>
                          <span className="text-xs font-medium">{data.utilization}%</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-secondary rounded-full transition-all duration-1000"
                            style={{ width: `${data.utilization}%`, animationDelay: `${index * 0.2}s` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Benefits & CTA */}
          <div className="space-y-8">
            <div>
              <h3 className="text-2xl font-display font-bold mb-6">Key Benefits</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="p-1 rounded-full bg-secondary/20 mt-1">
                    <div className="w-2 h-2 bg-secondary rounded-full" />
                  </div>
                  <div>
                    <h4 className="font-semibold">85% Time Reduction</h4>
                    <p className="text-sm text-muted-foreground">in manual scheduling processes</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="p-1 rounded-full bg-primary/20 mt-1">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                  </div>
                  <div>
                    <h4 className="font-semibold">Better Resource Utilization</h4>
                    <p className="text-sm text-muted-foreground">optimized fleet deployment</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="p-1 rounded-full bg-secondary/20 mt-1">
                    <div className="w-2 h-2 bg-secondary rounded-full" />
                  </div>
                  <div>
                    <h4 className="font-semibold">Real-Time Monitoring</h4>
                    <p className="text-sm text-muted-foreground">live performance tracking</p>
                  </div>
                </div>
              </div>
            </div>

            <Card className="gradient-card border-0 shadow-medium">
              <CardContent className="p-8 text-center">
                <PieChart className="w-12 h-12 text-primary mx-auto mb-4" />
                <h4 className="text-xl font-bold mb-2">Comprehensive Reports</h4>
                <p className="text-muted-foreground mb-6">
                  Get detailed analytics reports with actionable insights and recommendations.
                </p>
                <Button 
                  size="lg" 
                  className="w-full gradient-hero text-white border-0 hover:opacity-90 hover-lift"
                >
                  <Download className="mr-2 w-4 h-4" />
                  Get Report PDF
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ReportsSection;