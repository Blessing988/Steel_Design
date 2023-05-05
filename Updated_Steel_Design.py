#!/usr/bin/env python
# coding: utf-8

# In[6]:


import numpy as np
import pandas as pd 


# In[7]:


data = pd.read_csv("UB_dimensions.csv")
data.head(10)


# In[8]:


class UB:
    def __init__(self, length, beam_type, Py=275, E=205):
        self.length = length
        self.beam_type = beam_type
        self.Py = Py
        self.E = E


# In[9]:


class UDL:
    def __init__(self, load_type, value):
        # load_type can be dead load or live load 
        self.load_type = load_type
        self.value = value 


# In[10]:


class PointLoad:
    def __init__(self, load_type, value, distance):
        # load_type can be dead load or live load 
        # distance : distance of the load from the left support
        self.load_type = load_type
        self.value = value
        self.distance = distance


# In[11]:


class Analyze():
    def __init__(self, ub, list_of_udl, list_of_PL=None):
        self.list_of_udl = list_of_udl
        self.list_of_PL = list_of_PL
        self.ub = ub 
        
        self.Gk = []  # list of the intensities of the dead loads
        self.Qk = []   # list of the intensities of the live loads
        self.P_LL = [] # list of the values of the point loads which are live loads
        self.P_DL = []  # list of the values of point loads which are dead loads
        self.a_ll = []
        self.b_ll = []
        self.a_dl = []
        self.b_dl = []
        
        L = self.ub.length 
        
        # Appending the values of all the udls to a list
        sample = [self.Gk.append(udl.value) if udl.load_type=="dead_load" else self.Qk.append(udl.value) for udl in self.list_of_udl]
        # Appending the values of all the point loads to a list
        if self.list_of_PL is not None:
            sample = [self.P_DL.append(PL.value) if PL.load_type=="dead_load" else self.P_LL.append(PL.value) for PL in self.list_of_PL]
            # Appending the values of a from the point dead and live loads to a list
            sample = [self.a_dl.append(PL.distance) if PL.load_type=="dead_load" else self.a_ll.append(PL.distance) for PL in self.list_of_PL]
            # Appending the values of b from the point dead and live loads to a list
            sample = [self.b_dl.append(L-PL.distance) if PL.load_type=="dead_load" else self.b_ll.append(L-PL.distance) for PL in self.list_of_PL]
        else:
            self.P_LL = [0]
            self.P_DL = [0]
            self.a_ll = [0]
            self.b_ll = [0]
            self.a_ll = [0]
            self.b_dl = [0]
    
    def choose_a_section(self):
        Gk = np.array(self.Gk)
        Qk = np.array(self.Qk)
        P_LL = np.array(self.P_LL)
        P_DL = np.array(self.P_DL)
        a_ll = np.array(self.a_ll)
        a_dl = np.array(self.a_dl)
        b_ll = np.array(self.b_ll)
        b_dl = np.array(self.b_dl)
        
        L = self.ub.length
        b_dl = L - a_dl
        b_ll = L - a_ll
        # Calculating the theoretical bending moment 
        
        if self.ub.beam_type == "simply-supported":
            M = np.sum((1.4*Gk*L**2)/8) + np.sum((1.6*Qk*L**2)/8) + np.sum((1.6*P_LL*a_ll*b_ll)/L) + np.sum((1.4*P_DL*a_dl*b_dl)/L)
        elif self.ub.beam_type == "cantilever":
            M = np.sum((1.4*Gk*L**2)/2) + np.sum((1.6*Qk*L**2)/2) + np.sum((1.6*P_LL*a_ll)) + np.sum((1.4*P_DL*a_dl))
            
        # Determining Sxx
        Sxx = (M * 10**3)/self.ub.Py
        
        self.sections = []
        data.sort_values('S_xx(cm3)', inplace=True)
        for value in data["S_xx(cm3)"]:
            if value >= Sxx:
                self.sections.append(data[data["S_xx(cm3)"] == value].Dimension)
        sec_1 = self.sections[:3][0].values[0]
        sec_2 = self.sections[:3][1].values[0]
        sec_3 = self.sections[:3][2].values[0]
        """
        print("We can choose any of the following sections :\n")
        print("{}".format(sec_1))
        print("{}".format(sec_2))
        print("{}\n".format(sec_3))
        self.sec_1 = se
        """
        
        # print("We will choose {} for our analysis".format(self.sec_1))
        return sec_1

    def classify_the_section(self):
        section = self.choose_a_section()
        
        # eccentricity
        e = (275/self.ub.Py)**0.5 
        
        section_type = {}
        
        # Checking the flange
        b_over_T = data[data["Dimension"]==section]["b/T"].values[0]
        
        if b_over_T <= 8.5 * e:
            result_f = "plastic"
        elif (b_over_T > 8.5*e) and (b_over_T <= 9.5*e):
            result_f = "compact"
        elif (b_over_T > 9.5*e) and (b_over_T <= 15*e):
            result_f = "semi-compact"
        
        # Checking our web 
        d_over_t = data[data["Dimension"]==section]["d/t"].values[0]
        if d_over_t <= 79 * e:
            result_w = "plastic"
        elif (d_over_t > 79*e) and (d_over_t <= 98*e):
            result_w = "compact"
        elif (d_over_T > 98*e) and (b_over_T <= 120*e):
            result_w = "semi-compact"
        
        section_type["flange"] = result_f
        section_type["web"] = result_w
        return section_type

    def max_Shear_Moment(self):
        Gk = np.array(self.Gk)
        Qk = np.array(self.Qk)
        P_LL = np.array(self.P_LL)
        P_DL = np.array(self.P_DL)
        a_ll = np.array(self.a_ll)
        a_dl = np.array(self.a_dl)
        b_ll = np.array(self.b_ll)
        b_dl = np.array(self.b_dl)
        section = self.choose_a_section()
        
        L = self.ub.length
        # dictionary for maximum shear and bending moment
        max_dict = {}
        
        # Extract the mass per metre for the selected section
        mass_per_metre = data[data["Dimension"]==section]["mass_per_metre"].values[0]
    
        # Self-weight of the beam (in kN/m)
        SW = (mass_per_metre * 9.81*L)/1000
        
        # Determining the Maximum shear force
        
        
        # Total load due to live load and dead load(UDL)
        load_gk_and_qk= np.sum(1.4*Gk*L) + np.sum(1.6*Qk*L)
        
        # Total load due to point load
        load_LL = 1.6*P_LL
        load_DL = 1.4*P_DL
    
        if self.ub.beam_type == "simply-supported":
            shear_forces = []
            
            # Reaction at left support
            Ra = load_gk_and_qk/2 + np.sum(load_LL*b_ll/L) + np.sum(load_DL*b_dl/L)
            
            # Reaction at the right support
            Rb = load_gk_and_qk/2 + np.sum(load_LL*a_ll/L) + np.sum(load_DL*a_dl/L)
            
            # Putting reactions in a list
            shear_forces.append(Ra + 1.4*SW/2)
            shear_forces.append(Rb + 1.4*SW/2)
            
            max_shear = max(shear_forces)
        
#             if (Ra == Rb):
#                 print("Shear is the same at both left and right support and the value is {}kN".format(max_shear))
#             elif Ra > Rb:
#                 print("Shear is maximum at the left support and the value is {}kN".format(max_shear))
#             elif Rb > Ra:
#                 print("Shear is maximum at the right support and the value is {}kN".format(max_shear))
        
        if self.ub.beam_type == "cantilever":
            
            # Maximum_shear
            max_shear = load_gk_and_qk + np.sum(load_LL) + np.sum(load_DL) + 1.4*SW
            
        #return max_shear
        
        # Determining the Maximum Bending Moment
        if self.ub.beam_type == "simply-supported":
            
            # Moment due to loading
            moment_load = np.sum((1.4*Gk*L**2)/8) + np.sum((1.6*Qk*L**2)/8) + np.sum((load_LL*a_ll*b_ll)/L) + np.sum((load_DL*a_dl*b_dl)/L)
            
            # Moment due to Self-weight or the beam
            SW_moment = 1.4*(SW/L)*(L**2)/8
            
            # Overall moment
            total_moment = moment_load + SW_moment
            
        if self.ub.beam_type == "cantilever":
            
            # Moment due to loading
            moment_load = np.sum((1.4*Gk*L**2)/2) + np.sum((1.6*Qk*L**2)/2) + np.sum((load_LL*a_ll)) + np.sum((load_DL*a_dl))
            
            # Moment due to Self-weight or the beam
            SW_moment = 1.4*(SW/L)*(L**2)/2
            
            # Overall moment
            total_moment = moment_load + SW_moment
            
        max_dict["Maximum Shear Force"] = max_shear
        max_dict["Maximum Moment"] = total_moment
        
        return max_dict
            
    
    def shear_check(self):
        section = self.choose_a_section()
        t = data[data["Dimension"]==section]["t(mm)"].values[0]
        D = data[data["Dimension"]==section]["D(mm)"].values[0]
        
        # Calculating the shear capacity in kN
        Pv = 0.6*self.ub.Py*t*D*(10**-3)
        # Extracting the maximum shear force (Fv)
        Fv = round(self.max_Shear_Moment()["Maximum Shear Force"], 4)
        
        # Checking whether the section will undergo shear failure 
        if Fv > Pv:
            return ["The section has failed Shear and hence it is inadequate", Fv, Pv]
            
        else:
            return ["Shear is okay", Fv, Pv]
    
    def bending_check(self):
        section = self.choose_a_section()
        
        # Type of section (whether plastic or compact or semi-compact)
        f_type = self.classify_the_section()["flange"] # type of flange
        w_type= self.classify_the_section()["web"] # type of web
        
        
        # Extracting the maximum shear force (Fv)
        Fv = round(self.max_Shear_Moment()["Maximum Shear Force"], 4)
        
        # Extracting the maximum moment(M)
        M  = round(self.max_Shear_Moment()["Maximum Moment"], 4)
        
        t = data[data["Dimension"]==section]["t(mm)"].values[0]
        D = data[data["Dimension"]==section]["D(mm)"].values[0]
        Sxx = data[data["Dimension"]==section]["S_xx(cm3)"].values[0]
        Zxx = data[data["Dimension"]==section]["S_xx(cm3)"].values[0]
        
        # Calculating the shear capacity in kN
        Pv = 0.6*self.ub.Py*t*D*(10**-3)
         
        if Fv <= Pv:
            # Low Shear
            if Fv <= 0.6*Pv:
                print("There is low shear and it has a value of {} kN".format(Fv))
                #Moment capacity 
                
                # Plastic or compact section 
                if (f_type == 'plastic' and w_type == 'plastic') or (f_type == "plastic" and w_type=="compact") or (f_type=="compact" and w_type=="plastic") or (f_type=="compact" and w_type=="compact"): 
                    Mc = round(self.ub.Py*Sxx*10**-3, 4)
                    if (M <= Mc) and (Mc <= 1.2*self.ub.Py*Zxx*10**-3):
                        print("Bending is okay. The applied Moment({} kNm) is less than the Moment Capacity({} kNm)".format(M, Mc))
                    else:
                        print("The section has failed Bending Check. Change the section")
                        
                # Semi-compact sections
                elif (f_type == 'plastic' and w_type == 'semi-compact') or (f_type == "semi-compact" and w_type=="plastic") or (f_type=="compact" and w_type=="semi-compact") or (f_type=="semi-compact" and w_type=="compact") or (f_type=="semi-compact" and w_type=="semi-compact"):
                    Mc = self.ub.Py*Zxx*10**-3
                    if M <= Mc:
                        print("Bending is okay")
                    else:
                        print("The section has failed Bending Check. Change the section")
            else:
                print("There is high shear and it has a value of {} kN".format(Fv))
                
                # Plastic or Compact Section 
                if (f_type == 'plastic' and w_type == 'plastic') or (f_type == "plastic" and w_type=="compact") or (f_type=="compact" and w_type=="plastic") or (f_type=="compact" and w_type=="compact"): 
                    
                    Sv = t*(D**2)/4  # reduced moment capacity
                    p1 = (2.5*Fv)/Pv - 1.5
                    Mc = self.ub.Py*(Sxx - Sv*p1)*10**-3
                    
                    if (M <= Mc) and (Mc <= 1.2*Py*Zxx*10**-3) :
                        print("Bending is okay")
                    else:
                        print("The section has failed Bending Check. Change the section")
                        
                # Semi-compact sections        
                elif (f_type == 'plastic' and w_type == 'semi-compact') or (f_type == "semi-compact" and w_type=="plastic") or (f_type=="compact" and w_type=="semi-compact") or (f_type=="semi-compact" and w_type=="compact") or (f_type=="semi-compact" and w_type=="semi-compact"):
                    Mc = self.ub.Py*Zxx*10**-3
                    if M <= Mc:
                        print("Bending is okay")
                    else:
                        print("The section has failed Bending Check. Change the section") 

    def deflection_check(self):
        # for deflection the `applied deflection` should be <= `allowable deflection`
        
        section = self.choose_a_section()  # Chosen section
        
        L = self.ub.length  
        E = self.ub.E
        a = np.array(self.a_ll)
        b = L-a
        I = data[data["Dimension"]==section]["I_xx(cm4)"].values[0] # Second moment of area
        
        # load intensity for the live load 
        w = np.array(self.Qk)
        
        # Additional load if there is a characteristic imposed load
        P = np.array(self.P_LL)
        
        if self.ub.beam_type == "simply-supported":
            all_deflection = (L*1000)/360  # allowable deflection in mm 
            
            # deflection to live load only
            LL_def = np.sum((5*w*L**4)/ (384*E*I))
            
            total_add_def = []
            for (i, (a, b)) in enumerate(zip(a, b)):
                if a < b:
                    c = ((1/3)*b*(L+a))**0.5
                    add_def = (P[i]*a*c**3)/(3*L*E*I)  # deflection due to additional live load
                    total_add_def.append(add_def)
                elif a > b :
                    c = ((1/3)*(L**2 - b**2))**0.5
                    add_def = (P[i]*b*c**3)/(3*L*E*I)
                elif a == b :
                    add_def = (P[i]*L**3)/(48*E*I)
                    total_add_def.append(add_def)
            # Applied deflection
            app_deflection = round((LL_def + np.sum(total_add_def))*10**5, 4)
            
        elif self.ub.beam_type == "cantilever":
            all_deflection = round((L*1000)/180, 4)  # allowable deflection in mm 
            
            # deflection due to live load only
            LL_def = np.sum((w*L**4) / (8*E*I))
            
             # deflection due to additional live load
            add_def = np.sum(((P*a**2)*(3*L - a))/(6*E*I) )
            
            app_deflection = round((LL_def + add_def)*10**5, 4)
        
        # Comparing the applied deflection to the allowable deflection
        if app_deflection <= all_deflection :
            print("Deflection is okay.The applied deflection({} mm) is <= the allowable delection({} mm)".format(app_deflection, all_deflection))
        else:
            print("The section has failed Deflection Check. Change the section")
            
    def web_bearing_or_buckling(self, b1, be=0):
        # b1 is the stiff bearing length
        # be the the distance to the end of the member from the end of the stiff bearing 
        
        section = self.choose_a_section()
        Py = self.ub.Py
        # Getting the thickness of the flange
        T = data[data["Dimension"]==section]["T(mm)"].values[0]
        # Getting the root radius
        r = data[data["Dimension"]==section]["r(mm)"].values[0]
        # web thickness
        t = data[data["Dimension"]==section]["t(mm)"].values[0]
        # depth between the fillets
        d = data[data["Dimension"]==section]["d(mm)"].values[0]
        # Extracting the maximum Shear Force
        Fv = round(self.max_Shear_Moment()["Maximum Shear Force"], 4)
        
        k = (T + r) # for rolled I - or H sections
        n = 2 + 0.6*(be/k) 
        
        # Bearing Capacity 
        Pb = (b1 + n*k)*t*Py*10**-3
        
        if Fv <= Pb :
            print("Web bearing is okay")
        else:
            print("The section has failed web bearing check.Change the section or provide web stiffness")
            
        # Check for contact stress at the support 
        Pcs = (b1 + 2*(r+T))*Py
        
        """
        if Fv <= Pcs :
            print("Contact Stress at support is okay")
        else:
            print("The section failed Contact stress check. Stress at the contact support isn't good")
        """
        
        # Web buckling 
        ae = be + (b1/2)  # distance from the concentrated load or reaction to the nearer end of the member
        e = (275/Py)**0.5
        
        if ae < 0.7*d:
            # Buckling resistance
            Px = (((ae + 0.7*d)/1.4*d) * (25*e*t/np.sqrt((b1 + n*k)*d))*Pb)*10**-3
            
        elif ae >= 0.7*d:
            Px = ((25*e*t/np.sqrt((b1 + n*k)*d))*Pb)*10**-3
            
        if Fv <= Px :
            print("Web buckling is okay")
        else:
            print("The section has failed web buckling check. Change the section or provide web stiffness")
    
    def lateral_torsional_buckling(self):
        pass        



