#include "TString.h"
#include "TObjArray.h"
#include "TObjString.h"
#include <TSystem.h>
#include <iostream>
#include "TFile.h"
#include "TDirectoryFile.h"
#include "TH1F.h"
#include "TObject.h"
#include <signal.h>

//Usage: ScaleAllHist("template_sgn.root,template_int.root",100./35.9)

int ScaleAllHist(TString input, Double_t factor){
 TObjArray *files = input.Tokenize(",");
 for (Int_t i = 0; i < files->GetEntries(); i++) {
   TString file = ((TObjString*)files->At(i))->String();
   TString nfile1 = file;
   nfile1.ReplaceAll(".root","");
   TString nfile ;
   nfile.Form("%s_scaled_by_%.2f.root",nfile1.Data(),factor);
   gSystem->CopyFile(file,nfile,-1);
   TFile* f = new TFile(nfile,"UPDATE");
   std::cout<<"Loading file: "<<file<<" Scaling factor: "<<factor<<"\n";
   std::cout<<"Update file: "<<nfile<<" Scaling factor: "<<factor<<"\n";
   TList* l = f->GetListOfKeys();
   for (Int_t i = 0; i < l->GetEntries(); i++) {
     TString category = l->At(i)->GetName();
     TDirectoryFile* tdir = (TDirectoryFile*) f->Get(category);
     tdir->cd();
     TList* shapes = tdir->GetListOfKeys();
     std::cout<<"Doing category: "<<category<<"\n";
     Int_t n = shapes->GetEntries();
     for (Int_t j = 0; j < n; j++) {
       TString shape = shapes->At(j)->GetName();
       TH1F * h = (TH1F *)tdir->Get(shape);
       h->Scale(factor);
       h->Write(shape,TObject::kWriteDelete);
     } 
   }
   f->Close();
   delete f;
 }
 return 0;
}
