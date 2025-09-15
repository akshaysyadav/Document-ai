import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Train, 
  Users, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  MapPin, 
  Zap,
  RefreshCw,
  Settings,
  Bell
} from "lucide-react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const Dashboard = () => {
  const liveStats = [
    {
      icon: <Train className="w-6 h-6" />,
      title: "Active Trains",
      value: "24",
      total: "28",
      status: "operational"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Current Passengers",
      value: "12,847",
      trend: "+3.2%",
      status: "normal"
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "System Uptime",
      value: "99.8%",
      duration: "23d 14h",
      status: "excellent"
    },
    {
      icon: <AlertTriangle className="w-6 h-6" />,
      title: "Active Alerts",
      value: "2",
      type: "Minor",
      status: "warning"
    }
  ];

  const activeTrains = [
    {
      id: "TR-001",
      route: "Aluva → Pettah",
      currentStation: "Kaloor",
      nextStation: "Lissie",
      passengers: "187/240",
      status: "On Time",
      eta: "2 min",
      delay: null
    },
    {
      id: "TR-002", 
      route: "Pettah → Aluva",
      currentStation: "MG Road",
      nextStation: "Maharaja's",
      passengers: "203/240",
      status: "Delayed",
      eta: "5 min",
      delay: "3 min"
    },
    {
      id: "TR-003",
      route: "Aluva → Pettah", 
      currentStation: "Edapally",
      nextStation: "Changampuzha Park",
      passengers: "156/240",
      status: "On Time",
      eta: "1 min",
      delay: null
    },
    {
      id: "TR-004",
      route: "Pettah → Aluva",
      currentStation: "Ernakulam South",
      nextStation: "Kadavanthra",
      passengers: "221/240",
      status: "On Time", 
      eta: "3 min",
      delay: null
    }
  ];

  const systemAlerts = [
    {
      id: "ALT-001",
      type: "Maintenance",
      station: "Kaloor Station",
      message: "Scheduled cleaning in progress - Platform 2",
      priority: "Low",
      time: "10 min ago"
    },
    {
      id: "ALT-002",
      type: "Passenger",
      station: "MG Road Station", 
      message: "High passenger volume detected - Extra staff deployed",
      priority: "Medium",
      time: "25 min ago"
    }
  ];

  const stationStatus = [
    { name: "Aluva", status: "Operational", passengers: "523", capacity: 85 },
    { name: "Pettah", status: "Operational", passengers: "672", capacity: 92 },
    { name: "MG Road", status: "Busy", passengers: "891", capacity: 98 },
    { name: "Kaloor", status: "Operational", passengers: "445", capacity: 76 },
    { name: "Edapally", status: "Operational", passengers: "334", capacity: 65 }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="pt-20">
        {/* Dashboard Header */}
        <section className="bg-gradient-to-r from-primary to-secondary text-white py-12">
          <div className="container mx-auto px-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-display font-bold mb-2">
                  Metro Operations Dashboard
                </h1>
                <p className="text-xl text-white/90">
                  Real-time monitoring of KMRL metro system
                </p>
              </div>
              <div className="flex gap-4">
                <Button variant="secondary">
                  <Bell className="w-5 h-5 mr-2" />
                  Alerts (2)
                </Button>
                <Button variant="outline" className="border-white text-white hover:bg-white hover:text-primary">
                  <RefreshCw className="w-5 h-5 mr-2" />
                  Refresh
                </Button>
                <Button variant="outline" className="border-white text-white hover:bg-white hover:text-primary">
                  <Settings className="w-5 h-5 mr-2" />
                  Settings
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Live Stats */}
        <section className="py-12 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {liveStats.map((stat, index) => (
                <Card key={index} className="hover-lift">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-lg bg-primary/10 text-primary">
                        {stat.icon}
                      </div>
                      <Badge 
                        variant={
                          stat.status === "excellent" ? "default" :
                          stat.status === "warning" ? "destructive" :
                          "secondary"
                        }
                      >
                        {stat.status === "operational" && <CheckCircle className="w-3 h-3 mr-1" />}
                        {stat.status === "warning" && <AlertTriangle className="w-3 h-3 mr-1" />}
                        {stat.status === "excellent" && <Zap className="w-3 h-3 mr-1" />}
                        {stat.status}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-2xl font-bold text-foreground">
                        {stat.value}
                        {stat.total && <span className="text-lg text-muted-foreground">/{stat.total}</span>}
                      </h3>
                      <p className="font-medium text-foreground">{stat.title}</p>
                      {stat.trend && (
                        <p className="text-sm text-secondary font-medium">{stat.trend}</p>
                      )}
                      {stat.duration && (
                        <p className="text-sm text-muted-foreground">{stat.duration}</p>
                      )}
                      {stat.type && (
                        <p className="text-sm text-muted-foreground">{stat.type} issues</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Active Trains and Alerts */}
        <section className="py-12">
          <div className="container mx-auto px-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Active Trains */}
              <div className="lg:col-span-2">
                <Card className="shadow-strong">
                  <CardHeader>
                    <CardTitle className="text-2xl text-foreground flex items-center gap-2">
                      <Train className="w-6 h-6" />
                      Live Train Status
                    </CardTitle>
                    <CardDescription>Real-time tracking of active metro trains</CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="space-y-4 p-6">
                      {activeTrains.map((train) => (
                        <div key={train.id} className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-smooth">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <Badge variant="outline">{train.id}</Badge>
                              <span className="font-medium text-foreground">{train.route}</span>
                            </div>
                            <Badge 
                              variant={train.status === "On Time" ? "default" : "destructive"}
                            >
                              {train.status === "On Time" ? (
                                <CheckCircle className="w-3 h-3 mr-1" />
                              ) : (
                                <AlertTriangle className="w-3 h-3 mr-1" />
                              )}
                              {train.status}
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div className="flex items-center gap-2">
                              <MapPin className="w-4 h-4 text-primary" />
                              <div>
                                <p className="text-muted-foreground">Current:</p>
                                <p className="font-medium">{train.currentStation}</p>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-secondary" />
                              <div>
                                <p className="text-muted-foreground">Next in:</p>
                                <p className="font-medium">{train.eta}</p>
                                {train.delay && (
                                  <p className="text-destructive text-xs">+{train.delay}</p>
                                )}
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <Users className="w-4 h-4 text-muted-foreground" />
                              <div>
                                <p className="text-muted-foreground">Passengers:</p>
                                <p className="font-medium">{train.passengers}</p>
                              </div>
                            </div>
                          </div>
                          
                          <div className="mt-3">
                            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                              <span>Next: {train.nextStation}</span>
                              <span>{Math.round((parseInt(train.passengers.split('/')[0]) / parseInt(train.passengers.split('/')[1])) * 100)}% capacity</span>
                            </div>
                            <Progress 
                              value={(parseInt(train.passengers.split('/')[0]) / parseInt(train.passengers.split('/')[1])) * 100} 
                              className="h-2"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* System Alerts */}
              <div>
                <Card className="shadow-medium mb-6">
                  <CardHeader>
                    <CardTitle className="text-xl text-foreground flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      System Alerts
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {systemAlerts.map((alert) => (
                      <div key={alert.id} className="p-3 border border-border rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <Badge 
                            variant={alert.priority === "High" ? "destructive" : 
                                    alert.priority === "Medium" ? "default" : "secondary"}
                          >
                            {alert.priority}
                          </Badge>
                          <span className="text-xs text-muted-foreground">{alert.time}</span>
                        </div>
                        <h4 className="font-medium text-foreground text-sm mb-1">
                          {alert.type} - {alert.station}
                        </h4>
                        <p className="text-sm text-muted-foreground">{alert.message}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Station Status */}
                <Card className="shadow-medium">
                  <CardHeader>
                    <CardTitle className="text-xl text-foreground flex items-center gap-2">
                      <MapPin className="w-5 h-5" />
                      Station Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {stationStatus.map((station, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{station.name}</span>
                          <Badge 
                            variant={station.status === "Busy" ? "destructive" : "secondary"}
                          >
                            {station.status}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                          <span>{station.passengers} passengers</span>
                          <span>{station.capacity}% capacity</span>
                        </div>
                        <Progress value={station.capacity} className="h-2" />
                      </div>
                    ))}
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

export default Dashboard;