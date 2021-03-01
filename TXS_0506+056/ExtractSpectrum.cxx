void ExtractSpectrum();

void ExtractSpectrum() {

	//Read in the source file, extract the Canvas, and save the histogram
	TFile * f1 = new TFile("source_counts_spectrum.root");
	TCanvas * C = (TCanvas*)f1->Get("c1");
	TH1D * hist1 = (TH1D*)C->GetPrimitive("EnergySpectrum");

	//Re draw the histogram
	TCanvas * C1 = new TCanvas();
	hist1->Draw();

	//Read in the background file, extract the Canvas, and save the histogram
	TFile * f2 = new TFile("background_counts_spectrum.root");
	TCanvas * C2 = (TCanvas*)f2->Get("c1");
	TH1D * hist2 = (TH1D*)C2->GetPrimitive("EnergySpectrum");

	//Re draw the histogram
	TCanvas * C3 = new TCanvas();
	hist2->Draw();
		
	//write to file:
	ofstream myfile;
	myfile.open ("extracted_spectrum.dat");
	myfile<<"EC[keV] EL[keV] EH[keV] BW[keV] src_ct/keV bg_ct/keV"<<endl;
	
	//Print the counts for each bin
	//skip first bin
	cout<<"Bin, Energy, Counts"<<endl;
	for (int i = 1; i < hist1->GetNbinsX(); i++) {
		
		//get bin information:
		cout<<i<<", "<<hist1->GetXaxis()->GetBinCenter(i)<<", "<<hist1->GetBinContent(i)<<endl; //for bin center
		cout<<i<<", "<<hist1->GetXaxis()->GetBinWidth(i)<<", "<<hist1->GetBinContent(i)<<endl; //for bin widths
		cout<<i<<", "<<hist1->GetXaxis()->GetBinLowEdge(i)<<", "<<hist1->GetBinContent(i)<<endl; //for bin lower edge
		cout<<i<<", "<<hist1->GetXaxis()->GetBinUpEdge(i)<<", "<<hist1->GetBinContent(i)<<endl; //for bin upper edge
		
		//write to file:
		myfile<<hist1->GetXaxis()->GetBinCenter(i)<<"\t"<<hist1->GetXaxis()->GetBinLowEdge(i)<<"\t"<<hist1->GetXaxis()->GetBinUpEdge(i)<<"\t"<<hist1->GetXaxis()->GetBinWidth(i)<<"\t"<<hist1->GetBinContent(i)<<"\t"<<hist2->GetBinContent(i)<<endl;
	
	}

}

