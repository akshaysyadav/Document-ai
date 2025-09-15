import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { FileText, Upload, Search, Tag, Clock, CheckCircle, Eye, Download } from "lucide-react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const Documents = () => {
  const recentDocuments = [
    {
      id: "DOC001",
      name: "Daily Operations Report - March 2024",
      type: "Operations Report",
      uploadedAt: "2 hours ago",
      status: "Processed",
      tags: ["Operations", "Daily", "March"],
      extractedData: "127 data points"
    },
    {
      id: "DOC002", 
      name: "Metro Safety Protocol Manual",
      type: "Safety Manual",
      uploadedAt: "1 day ago",
      status: "Processing",
      tags: ["Safety", "Protocol", "Manual"],
      extractedData: "Processing..."
    },
    {
      id: "DOC003",
      name: "Passenger Feedback Analysis Q1",
      type: "Feedback Report",
      uploadedAt: "3 days ago", 
      status: "Processed",
      tags: ["Feedback", "Analysis", "Q1"],
      extractedData: "89 data points"
    },
    {
      id: "DOC004",
      name: "Train Maintenance Schedule",
      type: "Maintenance",
      uploadedAt: "1 week ago",
      status: "Processed", 
      tags: ["Maintenance", "Schedule", "Train"],
      extractedData: "156 data points"
    }
  ];

  const automationFeatures = [
    {
      icon: <Upload className="w-6 h-6" />,
      title: "Smart Document Upload",
      description: "Drag and drop documents or scan directly. AI automatically categorizes and processes files.",
      stats: "99.9% accuracy"
    },
    {
      icon: <Search className="w-6 h-6" />,
      title: "Intelligent Search",
      description: "Find any document or data point instantly using natural language queries.",
      stats: "< 0.5s response time"
    },
    {
      icon: <Tag className="w-6 h-6" />,
      title: "Auto-Tagging",
      description: "Automatically categorize and tag documents based on content analysis.",
      stats: "15+ categories"
    },
    {
      icon: <FileText className="w-6 h-6" />,
      title: "Data Extraction",
      description: "Extract key information, metrics, and insights from any document type.",
      stats: "200+ data types"
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
                AI Document Automation
              </Badge>
              <h1 className="text-5xl font-display font-bold mb-6">
                Intelligent Document Management
              </h1>
              <p className="text-xl mb-8 text-white/90">
                Transform your metro operations with AI-powered document processing. 
                Automatically scan, extract, and organize all operational documents.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" variant="secondary" className="font-semibold">
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Documents
                </Button>
                <Button size="lg" variant="outline" 
                  className="border-white text-white hover:bg-white hover:text-primary">
                  <Eye className="w-5 h-5 mr-2" />
                  View Demo
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Upload Section */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto">
              <Card className="border-2 border-dashed border-primary/30 hover:border-primary/50 transition-smooth">
                <CardContent className="p-12 text-center">
                  <Upload className="w-16 h-16 text-primary mx-auto mb-6" />
                  <h3 className="text-2xl font-display font-bold mb-4 text-foreground">
                    Drop Documents Here
                  </h3>
                  <p className="text-muted-foreground mb-6 text-lg">
                    Upload PDF files, images, or scan documents directly. Our AI will process them automatically.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button size="lg" className="gradient-hero text-white">
                      <Upload className="w-5 h-5 mr-2" />
                      Choose Files
                    </Button>
                    <Button size="lg" variant="outline">
                      Scan Document
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-display font-bold mb-4 text-foreground">
                Automation Features
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Advanced AI capabilities that transform how you handle metro operational documents
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {automationFeatures.map((feature, index) => (
                <Card key={index} className="hover-lift">
                  <CardHeader>
                    <div className="flex items-center gap-4">
                      <div className="p-3 rounded-lg bg-primary/10 text-primary">
                        {feature.icon}
                      </div>
                      <div>
                        <CardTitle className="text-xl">{feature.title}</CardTitle>
                        <Badge variant="secondary" className="mt-1">
                          {feature.stats}
                        </Badge>
                      </div>
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

        {/* Search and Recent Documents */}
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="max-w-6xl mx-auto">
              {/* Search Bar */}
              <Card className="mb-12 shadow-medium">
                <CardContent className="p-6">
                  <div className="flex gap-4">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
                      <Input 
                        placeholder="Search documents, extract data, or ask questions..."
                        className="pl-12 h-14 text-lg"
                      />
                    </div>
                    <Button size="lg" className="gradient-hero text-white px-8">
                      Search
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Documents */}
              <Card className="shadow-strong">
                <CardHeader>
                  <CardTitle className="text-2xl text-foreground">Recent Documents</CardTitle>
                  <CardDescription>Recently processed metro operational documents</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="border-b border-border">
                        <tr className="bg-muted/30">
                          <th className="text-left p-4 font-semibold">Document</th>
                          <th className="text-left p-4 font-semibold">Type</th>
                          <th className="text-left p-4 font-semibold">Uploaded</th>
                          <th className="text-left p-4 font-semibold">Status</th>
                          <th className="text-left p-4 font-semibold">Tags</th>
                          <th className="text-left p-4 font-semibold">Extracted Data</th>
                          <th className="text-left p-4 font-semibold">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentDocuments.map((doc) => (
                          <tr key={doc.id} className="border-b border-border/50 hover:bg-muted/20">
                            <td className="p-4">
                              <div className="flex items-center gap-3">
                                <FileText className="w-5 h-5 text-primary" />
                                <div>
                                  <div className="font-medium text-foreground">{doc.name}</div>
                                  <div className="text-sm text-muted-foreground">{doc.id}</div>
                                </div>
                              </div>
                            </td>
                            <td className="p-4">
                              <Badge variant="outline">{doc.type}</Badge>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-2 text-muted-foreground">
                                <Clock className="w-4 h-4" />
                                {doc.uploadedAt}
                              </div>
                            </td>
                            <td className="p-4">
                              <Badge 
                                variant={doc.status === "Processed" ? "default" : "secondary"}
                              >
                                {doc.status === "Processed" && <CheckCircle className="w-3 h-3 mr-1" />}
                                {doc.status}
                              </Badge>
                            </td>
                            <td className="p-4">
                              <div className="flex flex-wrap gap-1">
                                {doc.tags.map((tag, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            </td>
                            <td className="p-4 text-muted-foreground">
                              {doc.extractedData}
                            </td>
                            <td className="p-4">
                              <div className="flex gap-2">
                                <Button size="sm" variant="ghost">
                                  <Eye className="w-4 h-4" />
                                </Button>
                                <Button size="sm" variant="ghost">
                                  <Download className="w-4 h-4" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Documents;