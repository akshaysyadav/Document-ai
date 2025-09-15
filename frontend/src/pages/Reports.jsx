import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { BarChart3, TrendingUp, Users, Clock, Train, Download, Calendar, RefreshCw } from "lucide-react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const Reports = () => {
  const kpiData = [
    {
      icon: <Train className="w-6 h-6" />,
      title: "Train Efficiency",
      value: "94.7%",
      change: "+2.3%",
      trend: "up",
      description: "Average on-time performance"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Daily Passengers",
      value: "187K",
      change: "+8.1%", 
      trend: "up",
      description: "Passengers served today"
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Average Wait Time",
      value: "3.2 min",
      change: "-12%",
      trend: "down",
      description: "Platform waiting time"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Revenue Growth",
      value: "₹2.4M",
      change: "+15.7%",
      trend: "up", 
      description: "Monthly revenue"
    }
  ];

  const chartData = [
    { month: "Jan", efficiency: 89, utilization: 78 },
    { month: "Feb", efficiency: 91, utilization: 82 },
    { month: "Mar", efficiency: 94, utilization: 85 },
    { month: "Apr", efficiency: 96, utilization: 88 },
    { month: "May", efficiency: 94, utilization: 90 },
    { month: "Jun", efficiency: 97, utilization: 92 }
  ];

  const reports = [
    {
      title: "Monthly Operations Report",
      description: "Comprehensive analysis of metro operations, efficiency metrics, and passenger statistics",
      type: "PDF",
      size: "2.4 MB",
      updated: "2 hours ago"
    },
    {
      title: "Passenger Flow Analysis",
      description: "Detailed breakdown of passenger patterns, peak hours, and route utilization",
      type: "Excel",
      size: "1.8 MB", 
      updated: "1 day ago"
    },
    {
      title: "Safety Incident Report",
      description: "Safety metrics, incident analysis, and preventive measures implementation",
      type: "PDF",
      size: "1.2 MB",
      updated: "3 days ago"
    },
    {
      title: "Revenue & Finance Report", 
      description: "Financial performance, ticket sales analysis, and revenue optimization insights",
      type: "PDF",
      size: "3.1 MB",
      updated: "1 week ago"
    }
  ];

  const benefits = [
    "Real-time operational insights and performance metrics",
    "Automated report generation with customizable parameters", 
    "Predictive analytics for demand forecasting",
    "Compliance reporting for regulatory requirements",
    "Interactive dashboards with drill-down capabilities"
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
                Analytics & Reporting
              </Badge>
              <h1 className="text-5xl font-display font-bold mb-6">
                Metro Performance Reports
              </h1>
              <p className="text-xl mb-8 text-white/90">
                Comprehensive analytics and insights for KMRL metro operations. 
                Track performance, analyze trends, and make data-driven decisions.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" variant="secondary" className="font-semibold">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  View Dashboard
                </Button>
                <Button size="lg" variant="outline" 
                  className="border-white text-white hover:bg-white hover:text-primary">
                  <Download className="w-5 h-5 mr-2" />
                  Download Reports
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* KPIs Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-display font-bold mb-4 text-foreground">
                Key Performance Indicators
              </h2>
              <p className="text-xl text-muted-foreground">
                Real-time metrics tracking metro operations performance
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {kpiData.map((kpi, index) => (
                <Card key={index} className="hover-lift">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-lg bg-primary/10 text-primary">
                        {kpi.icon}
                      </div>
                      <Badge 
                        variant={kpi.trend === "up" ? "default" : "secondary"}
                        className={kpi.trend === "up" ? "bg-secondary text-white" : ""}
                      >
                        {kpi.change}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-2xl font-bold text-foreground">{kpi.value}</h3>
                      <p className="font-medium text-foreground">{kpi.title}</p>
                      <p className="text-sm text-muted-foreground">{kpi.description}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Performance Trends Chart */}
        <section className="py-20">
          <div className="container mx-auto px-6">
            <Card className="max-w-6xl mx-auto shadow-strong">
              <CardHeader className="bg-gradient-to-r from-primary/5 to-secondary/5">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl text-foreground">Performance Trends</CardTitle>
                    <CardDescription>Monthly efficiency and utilization metrics</CardDescription>
                  </div>
                  <Button variant="outline" size="sm">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh Data
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-8">
                <div className="space-y-8">
                  {chartData.map((data, index) => (
                    <div key={index} className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-foreground">{data.month} 2024</h4>
                        <div className="flex gap-6 text-sm">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-primary"></div>
                            <span className="text-muted-foreground">Efficiency: {data.efficiency}%</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-secondary"></div>
                            <span className="text-muted-foreground">Utilization: {data.utilization}%</span>
                          </div>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Efficiency</span>
                            <span className="font-medium">{data.efficiency}%</span>
                          </div>
                          <Progress value={data.efficiency} className="h-2" />
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Utilization</span>
                            <span className="font-medium">{data.utilization}%</span>
                          </div>
                          <Progress value={data.utilization} className="h-2" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Available Reports */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-display font-bold mb-4 text-foreground">
                Available Reports
              </h2>
              <p className="text-xl text-muted-foreground">
                Download comprehensive reports and analysis
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
              {reports.map((report, index) => (
                <Card key={index} className="hover-lift">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <CardTitle className="text-xl">{report.title}</CardTitle>
                        <CardDescription>{report.description}</CardDescription>
                      </div>
                      <Badge variant="outline">{report.type}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">
                        <div className="flex items-center gap-4">
                          <span>{report.size}</span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {report.updated}
                          </span>
                        </div>
                      </div>
                      <Button>
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-20">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div>
                  <h2 className="text-3xl font-display font-bold mb-6 text-foreground">
                    Advanced Analytics Benefits
                  </h2>
                  <ul className="space-y-4">
                    {benefits.map((benefit, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <TrendingUp className="w-5 h-5 text-secondary mt-0.5 flex-shrink-0" />
                        <span className="text-muted-foreground">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <Card className="shadow-medium">
                  <CardHeader className="text-center">
                    <BarChart3 className="w-16 h-16 text-primary mx-auto mb-4" />
                    <CardTitle className="text-2xl">Generate Custom Report</CardTitle>
                    <CardDescription>
                      Create tailored reports based on your specific requirements
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="text-center">
                    <Button size="lg" className="gradient-hero text-white">
                      <Download className="w-5 h-5 mr-2" />
                      Create Report
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Reports;