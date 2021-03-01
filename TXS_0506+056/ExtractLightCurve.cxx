void ExtractLightCurve();

void ExtractLightCurve() {

	//Read in the file, extract the Canvas, and save the histogram
	TFile * f = new TFile("source_LC.root");
	TCanvas * C = (TCanvas*)f->Get("TimeOptimized");
	TH1D * hist = (TH1D*)C->GetPrimitive("TimeOptimized");

	//Re draw the histogram
	TCanvas * C1 = new TCanvas();
	hist->Draw();

	//write to file:
	ofstream myfile;
	myfile.open ("extracted_lc.dat");
	myfile<<"t_center[s] t_low[s] t_high[s] t_width[s] ct/s"<<endl;

	//Print the counts for each bin
	cout<<"Bin, Time, Counts"<<endl;
	for (int i = 1; i < hist->GetNbinsX(); i++) {
		cout<<i<<", "<<hist->GetXaxis()->GetBinCenter(i)<<", "<<hist->GetBinContent(i)<<endl; //for bin center
		cout<<i<<", "<<hist->GetXaxis()->GetBinWidth(i)<<", "<<hist->GetBinContent(i)<<endl; //for bin widths
		
		//write to file:
		myfile<<hist->GetXaxis()->GetBinCenter(i)<<"\t"<<hist->GetXaxis()->GetBinLowEdge(i)<<"\t"<<hist->GetXaxis()->GetBinUpEdge(i)<<"\t"<<hist->GetXaxis()->GetBinWidth(i)<<"\t"<<hist->GetBinContent(i)<<endl;
	}

}


