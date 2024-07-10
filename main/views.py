from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from main import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from pulp import *
from .forms import *
from .models import ProductionPlan
import xlwt
from io import BytesIO
from django.conf import settings
from django.contrib import messages
import plotly.graph_objects as go
from django.core.mail import send_mail

# Create your views here.
def index(request):    
    if request.method == "POST":
        if request.user.is_authenticated:
            inputName = str(request.POST.get('name'))
            inputMonthRange = int(request.POST.get('length'))
            queryCheck = ProductionPlan.objects.filter(name=inputName).exists()
            while queryCheck == True:
                inputName = inputName+'_copy'
                queryCheck = ProductionPlan.objects.filter(name=inputName).exists()
            ProductionPlan.objects.create(name=inputName, username=request.user, length=inputMonthRange)
            return redirect('planList')
        else:
            return redirect('login')
    return render(request, 'main/index.html')

@login_required(login_url='/login/')
def planList(request):
    searchColumn = request.GET.get("column")
    searchWord = request.GET.get("search")
    if searchColumn == "name" and searchWord:
        planList = ProductionPlan.objects.filter(username = request.user, name = searchWord).order_by('length')
    elif searchColumn == "length" and searchWord:
        planList = ProductionPlan.objects.filter(username = request.user, length = searchWord).order_by('length')
    else:
        planList = ProductionPlan.objects.filter(username = request.user).order_by('length')
    paginator = Paginator(planList, 5)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = paginator.page(paginator.num_pages)
    print(page_obj)
    return render(request, "main/planList.html", {'page_obj': page_obj})

def about(request):
    return render(request, "main/about.html")


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def deletePlan(request,plan_ID):
    plan = ProductionPlan.objects.filter(id=plan_ID, username=request.user)
    plan.delete()
    return redirect(planList)

def initiateOptimize(request, plan_ID):
    plan = ProductionPlan.objects.filter(id = plan_ID).values()
    return viewDetail(request, plan_ID, plan[0]["length"])

def initiateSensitivity(request, plan_ID):
    plan = ProductionPlan.objects.filter(id = plan_ID).values()
    return sensitivity(request, plan_ID, plan[0]["length"])

@login_required(login_url='/login/')
def inputVariables(request, plan_ID):
    if request.method == "POST":
        inputDemand1 = request.POST.get('demand1')
        inputDemand2 = request.POST.get('demand2')
        inputDemand3 = request.POST.get('demand3')
        inputDemand4 = request.POST.get('demand4')
        inputDemand5 = request.POST.get('demand5')
        inputDemand6 = request.POST.get('demand6')
        inputDemand7 = request.POST.get('demand7')
        inputDemand8 = request.POST.get('demand8')
        inputDemand9 = request.POST.get('demand9')
        inputDemand10 = request.POST.get('demand10')
        inputDemand11 = request.POST.get('demand11')
        inputDemand12 = request.POST.get('demand12')
        inputNumPermanent = request.POST.get('numPermanent')
        inputProdPermanent = request.POST.get('prodPermanent')
        inputProdTemporary = request.POST.get('prodTemporary')
        inputCostHiring = request.POST.get('costHiring')
        inputCostFiring = request.POST.get('costFiring')
        inputCostHoldingUnit = request.POST.get('costHoldingUnit')
        inputInventoryInitial = request.POST.get('inventoryInitial')
        inputInventoryFinal = request.POST.get('inventoryFinal')
        ProductionPlan.objects.filter(id=plan_ID).update(
            demand1 = inputDemand1, 
            demand2 = inputDemand2, 
            demand3 = inputDemand3, 
            demand4 = inputDemand4,
            demand5 = inputDemand5,
            demand6 = inputDemand6, 
            demand7 = inputDemand7, 
            demand8 = inputDemand8,
            demand9 = inputDemand9,
            demand10 = inputDemand10, 
            demand11 = inputDemand11, 
            demand12 = inputDemand12,
            numPermanent = inputNumPermanent,
            prodPermanent = inputProdPermanent,
            prodTemporary = inputProdTemporary,
            costHiring = inputCostHiring,
            costFiring = inputCostFiring,
            costHoldingUnit = inputCostHoldingUnit,
            inventoryInitial = inputInventoryInitial,
            inventoryFinal = inputInventoryFinal,
            filled = True
        )
        return redirect('planList')
    else:
        plan = ProductionPlan.objects.filter(id=plan_ID).values()
    return render(request, 'main/inputVariables.html',{'plan' : plan})

def viewDetail(request, plan_ID, num_months):
    status = optimize(plan_ID, num_months)  # Assume there's a generalized optimize function
    if status == 1:
        detail = ProductionPlan.objects.filter(id=plan_ID).values()
        for x in detail:
            total_hiring_cost = 0
            total_firing_cost = 0
            total_holding_cost = 0

            demands = []
            hiring_costs = []
            firing_costs = []
            holding_costs = []

            worker_numbers = [0]
            months = ['Start']
            for month in range(1, num_months + 1):
                demand = x[f'demand{month}'] - (x['numPermanent'] * x['prodPermanent'])
                if month == 1:
                    demand -= x['inventoryInitial']
                if demand < 0:
                    demand = 0
                demands.append(demand)
                
                hC = x[f'hiredTemporary{month}'] * x['costHiring']
                fC = x[f'firedTemporary{month}'] * x['costFiring']
                if month != num_months:
                    
                    ihc = x['costHoldingUnit'] * x[f'inventoryMonth{month}']
                    holding_costs.append(ihc)
                    total_holding_cost += ihc
                
                hiring_costs.append(hC)
                firing_costs.append(fC)

                total_hiring_cost += hC
                total_firing_cost += fC
                
                worker_numbers.append(x[f'numberTemporary{month}'])
                months.append(f'Month {month}')
            # FIGURES
            
            # Figure 1 : Total Cost Distribution (Malaysian Ringgit)
            labels = ['Inventory Holding Cost', 'Temp. Worker Hiring Cost', 'Temp. Worker Firing Cost']
            values = [total_holding_cost, total_hiring_cost, total_firing_cost]
            colors = ['#636efa', '#00cc96', '#ef553b']

            fig1Light = go.Figure(data=[go.Pie(labels=labels, textinfo='label+percent', values=values, hole=0.3, marker=dict(colors=colors))])
            fig1Light.update_layout(title='TOTAL COST DISTRIBUTION', showlegend=False)
            
            fig1Dark = go.Figure(data=[go.Pie(labels=labels, textinfo='label+percent', values=values, hole=0.3, marker=dict(colors=colors))])
            fig1Dark.update_layout(title='TOTAL COST DISTRIBUTION', showlegend=False, template='plotly_dark')
            
            # Figure 2 : Monthly Cost
            fig2Light = go.Figure(data=[
                go.Bar(name='Inventory Holding Cost', x=months[1:], y=holding_costs, marker=dict(color=colors[0])),
                go.Bar(name='Hiring Cost', x=months[1:], y=hiring_costs, marker=dict(color=colors[1])),
                go.Bar(name='Firing Cost', x=months[1:], y=firing_costs, marker=dict(color=colors[2])),
            ])
            fig2Light.update_layout(barmode='stack', title='MONTHLY COST', yaxis_title='Costs')

            fig2Dark = go.Figure(data=[
                go.Bar(name='Inventory Holding Cost', x=months[1:], y=holding_costs, marker=dict(color=colors[0])),
                go.Bar(name='Hiring Cost', x=months[1:], y=hiring_costs, marker=dict(color=colors[1])),
                go.Bar(name='Firing Cost', x=months[1:], y=firing_costs, marker=dict(color=colors[2])),
            ])
            fig2Dark.update_layout(barmode='stack', title='MONTHLY COST', yaxis_title='Costs', template='plotly_dark')

            # Figure 3 : Net Number of Temporary Workers per Month
            fig3Light = go.Figure(data=[go.Scatter(x=months, y=worker_numbers, mode='lines+markers', name="Number of Temporary Workers")])
            fig3Light.update_layout(title='Net Number of Temporary Workers per Month', yaxis_title='Net Number of Temporary Workers')
            
            fig3Dark = go.Figure(data=[go.Scatter(x=months, y=worker_numbers, mode='lines+markers', name="Number of Temporary Workers")])
            fig3Dark.update_layout(title='Net Number of Temporary Workers per Month', yaxis_title='Net Number of Temporary Workers', template='plotly_dark')

        return render(request, "main/viewDetail.html", {
            'detail': detail, 
            'demands': demands, 
            'holding_costs': holding_costs,
            'hiring_costs': hiring_costs, 
            'firing_costs': firing_costs, 
            'total_hiring_cost': total_hiring_cost, 
            'total_firing_cost': total_firing_cost, 
            'total_holding_cost': total_holding_cost, 
            'fig1Light' : fig1Light.to_html(full_html=False), 
            'fig1Dark' : fig1Dark.to_html(full_html=False), 
            'fig2Light' : fig2Light.to_html(full_html=False), 
            'fig2Dark' : fig2Dark.to_html(full_html=False), 
            'fig3Light' : fig3Light.to_html(full_html=False), 
            'fig3Dark' : fig3Dark.to_html(full_html=False)})
    elif status == 0:
        messages.error(request, "PLAN COULD NOT BE SOLVED")
    elif status == -1:
        messages.error(request, "PLAN IS NOT FEASIBLE")
    elif status == -2:
        messages.error(request, "PLAN RESULTS IS UNBOUNDED")
    elif status == -3:
        messages.error(request, "PLAN RESULTS IS UNDEFINED")
    return redirect(planList)

def sensitivity(request, plan_ID, num_months):
    detail = ProductionPlan.objects.filter(id=plan_ID).values()
    adDemands = []
    aiDemands = []
    decreasedDemands = []
    increasedDemands = []
    for x in detail:
        inputDemands = [int(x[f'demand{i+1}']) for i in range(num_months)]  # Adjust the range as needed
        inputNumPermanent = int(x['numPermanent'])
        inputProdPermanent = int(x['prodPermanent'])
        inputProdTemporary = int(x['prodTemporary'])
        inputCostHiring = float(x['costHiring'])
        inputCostFiring = float(x['costFiring'])
        inputCostHoldingUnit = float(x['costHoldingUnit'])
        inputInventoryInitial = int(x['inventoryInitial'])
        inputInventoryFinal = int(x['inventoryFinal'])
        inputOptimalCost = int(x['optimalCost'])
    
        for i in range(1, num_months + 1):
            # SENSITIVITY ANALYSIS START
            
            # Save Original Cost
            original_cost = inputOptimalCost
            
            original_demand = inputDemands[i-1]

            # Define perturbation step size
            step_size = min(inputProdPermanent, inputProdTemporary)
            
            # Initialize allowable increase and decrease
            aiDemand = 0
            adDemand = 0

            # Perform iterative perturbation
            iteration = 0
            while iteration < 100:
                # Perturb the variable value (increase)
                inputDemands[i-1] += step_size
                
                # Solve the modified LP problem
                month = list(range(num_months))
                monthIHC = list(range(num_months - 1))
                
                model = LpProblem("Minimize Cost", LpMinimize)
                
                ihcDict = LpVariable.dicts('IHC', monthIHC, lowBound=0, cat='Integer')
                hcDict = LpVariable.dicts('HC', month, lowBound=0, cat='Integer')
                fcDict = LpVariable.dicts('FC', month, lowBound=0, cat='Integer')
                ntwDict = LpVariable.dicts('NTW', month, lowBound=0, cat='Integer')
                
                model += (lpSum([inputCostHoldingUnit * ihcDict[i] for i in monthIHC]) + 
                        lpSum([inputCostHiring * hcDict[i] for i in month]) + 
                        lpSum([inputCostFiring * fcDict[i] for i in month]))
                
                if num_months == 1:
                    model.addConstraint(inputInventoryInitial + (inputProdTemporary * ntwDict[0]) == 
                                    inputDemands[0] - (inputNumPermanent * inputProdPermanent) + inputInventoryFinal, name='ihcCons1')
                else:
                    model.addConstraint(inputInventoryInitial + (inputProdTemporary * ntwDict[0]) == 
                                    inputDemands[0] - (inputNumPermanent * inputProdPermanent) + ihcDict[0], name='ihcCons1')
                
                    for i in range(1, num_months - 1):
                        model.addConstraint(ihcDict[i-1] + (inputProdTemporary * ntwDict[i]) == 
                                            inputDemands[i] - (inputNumPermanent * inputProdPermanent) + ihcDict[i], name=f'ihcCons{i+1}')
                    
                    model.addConstraint(ihcDict[num_months - 2] + (inputProdTemporary * ntwDict[num_months - 1]) == 
                                        inputDemands[num_months - 1] - (inputNumPermanent * inputProdPermanent) + inputInventoryFinal, name=f'ihcCons{num_months}')
                
                model.addConstraint(ntwDict[0] == hcDict[0] - fcDict[0], name='ntwCons1')
                
                if num_months > 1:
                    for i in range(1, num_months):
                        model.addConstraint(ntwDict[i] == ntwDict[i-1] + (hcDict[i] - fcDict[i]), name=f'ntwCons{i+1}')
                
                model.solve(pulp.PULP_CBC_CMD(timeLimit=5))
                
                # Check if the optimal solution changes
                if model.status == 1:
                    if value(model.objective) != original_cost:
                        aiDemand = step_size * iteration
                        break
                
                iteration += 1

            inputDemands[i-1] = original_demand

            # Perform iterative perturbation
            iteration = 0
            while iteration < 200:
                # Perturb the variable value (decrease)
                inputDemands[i-1] -= step_size  # Adjust it back to the original value first
                
                # Solve the modified LP problem
                month = list(range(num_months))
                monthIHC = list(range(num_months - 1))
                
                model = LpProblem("Minimize Cost", LpMinimize)
                
                ihcDict = LpVariable.dicts('IHC', monthIHC, lowBound=0, cat='Integer')
                hcDict = LpVariable.dicts('HC', month, lowBound=0, cat='Integer')
                fcDict = LpVariable.dicts('FC', month, lowBound=0, cat='Integer')
                ntwDict = LpVariable.dicts('NTW', month, lowBound=0, cat='Integer')
                
                model += (lpSum([inputCostHoldingUnit * ihcDict[i] for i in monthIHC]) + 
                        lpSum([inputCostHiring * hcDict[i] for i in month]) + 
                        lpSum([inputCostFiring * fcDict[i] for i in month]))
                
                if num_months == 1:
                    model.addConstraint(inputInventoryInitial + (inputProdTemporary * ntwDict[0]) == 
                                    inputDemands[0] - (inputNumPermanent * inputProdPermanent) + inputInventoryFinal, name='ihcCons1')
                else:
                    model.addConstraint(inputInventoryInitial + (inputProdTemporary * ntwDict[0]) == 
                                    inputDemands[0] - (inputNumPermanent * inputProdPermanent) + ihcDict[0], name='ihcCons1')
                
                    for i in range(1, num_months - 1):
                        model.addConstraint(ihcDict[i-1] + (inputProdTemporary * ntwDict[i]) == 
                                            inputDemands[i] - (inputNumPermanent * inputProdPermanent) + ihcDict[i], name=f'ihcCons{i+1}')
                    
                    model.addConstraint(ihcDict[num_months - 2] + (inputProdTemporary * ntwDict[num_months - 1]) == 
                                        inputDemands[num_months - 1] - (inputNumPermanent * inputProdPermanent) + inputInventoryFinal, name=f'ihcCons{num_months}')
                
                model.addConstraint(ntwDict[0] == hcDict[0] - fcDict[0], name='ntwCons1')
                
                if num_months > 1:
                    for i in range(1, num_months):
                        model.addConstraint(ntwDict[i] == ntwDict[i-1] + (hcDict[i] - fcDict[i]), name=f'ntwCons{i+1}')
                
                model.solve(pulp.PULP_CBC_CMD(timeLimit=5))
                
                # Check if the optimal solution changes
                if model.status == 1:
                    if value(model.objective) != original_cost:
                        adDemand = step_size * iteration
                        break
                
                iteration += 1

            inputDemands[i-1] = original_demand
            aiDemands.append(aiDemand)
            adDemands.append(adDemand)
            increasedDemands.append(inputDemands[i-1]+aiDemand)
            decreasedDemands.append(inputDemands[i-1]-adDemand)
        return render(request, "main/sensitivity.html", {
            'detail': detail, 
            'aiDemands': aiDemands, 
            'adDemands': adDemands,
            'increasedDemands': increasedDemands, 
            'decreasedDemands': decreasedDemands})

def optimize(plan_ID, num_months):
    detail = ProductionPlan.objects.filter(id=plan_ID).values()
    for x in detail:
        inputDemands = [int(x[f'demand{i+1}']) for i in range(num_months)]  # Adjust the range as needed
        inputNumPermanent = int(x['numPermanent'])
        inputProdPermanent = int(x['prodPermanent'])
        inputProdTemporary = int(x['prodTemporary'])
        inputCostHiring = float(x['costHiring'])
        inputCostFiring = float(x['costFiring'])
        inputCostHoldingUnit = float(x['costHoldingUnit'])
        inputInventoryInitial = int(x['inventoryInitial'])
        inputInventoryFinal = int(x['inventoryFinal'])

    month = list(range(num_months))
    monthIHC = list(range(num_months - 1))
    
    model = LpProblem("Minimize Cost", LpMinimize)
    
    ihcDict = LpVariable.dicts('IHC', monthIHC, lowBound=0, cat='Integer')
    hcDict = LpVariable.dicts('HC', month, lowBound=0, cat='Integer')
    fcDict = LpVariable.dicts('FC', month, lowBound=0, cat='Integer')
    ntwDict = LpVariable.dicts('NTW', month, lowBound=0, cat='Integer')
    
    model += (lpSum([inputCostHoldingUnit * ihcDict[i] for i in monthIHC]) + 
              lpSum([inputCostHiring * hcDict[i] for i in month]) + 
              lpSum([inputCostFiring * fcDict[i] for i in month]))
    
    if num_months == 1:
        model.addConstraint(inputInventoryInitial + (inputProdTemporary * ntwDict[0]) == 
                        inputDemands[0] - (inputNumPermanent * inputProdPermanent) + inputInventoryFinal, name='ihcCons1')
    else:
        model.addConstraint(inputInventoryInitial + (inputProdTemporary * ntwDict[0]) == 
                        inputDemands[0] - (inputNumPermanent * inputProdPermanent) + ihcDict[0], name='ihcCons1')
    
        for i in range(1, num_months - 1):
            model.addConstraint(ihcDict[i-1] + (inputProdTemporary * ntwDict[i]) == 
                                inputDemands[i] - (inputNumPermanent * inputProdPermanent) + ihcDict[i], name=f'ihcCons{i+1}')
        
        model.addConstraint(ihcDict[num_months - 2] + (inputProdTemporary * ntwDict[num_months - 1]) == 
                            inputDemands[num_months - 1] - (inputNumPermanent * inputProdPermanent) + inputInventoryFinal, name=f'ihcCons{num_months}')
    
    model.addConstraint(ntwDict[0] == hcDict[0] - fcDict[0], name='ntwCons1')
    
    if num_months > 1:
        for i in range(1, num_months):
            model.addConstraint(ntwDict[i] == ntwDict[i-1] + (hcDict[i] - fcDict[i]), name=f'ntwCons{i+1}')
    
    model.solve(pulp.PULP_CBC_CMD(timeLimit=5))
    optimizationStatus = model.status
    
    update_dict = {f'inventoryMonth{i+1}': ihcDict[i].varValue for i in range(num_months - 1)}
    update_dict.update({f'hiredTemporary{i+1}': hcDict[i].varValue for i in range(num_months)})
    update_dict.update({f'firedTemporary{i+1}': fcDict[i].varValue for i in range(num_months)})
    update_dict.update({f'numberTemporary{i+1}': ntwDict[i].varValue for i in range(num_months)})
    update_dict['optimalCost'] = value(model.objective)
    
    ProductionPlan.objects.filter(id=plan_ID).update(**update_dict)
    
    return optimizationStatus

style_head_row = xlwt.easyxf("""    
        align:
        wrap off,
        vert center,
        horiz center;
        borders:
        left THIN,
        right THIN,
        top THIN,
        bottom THIN;
        font:
        name Arial,
        colour_index white,
        bold on,
        height 0xA0;
        pattern:
        pattern solid,
        fore-colour 0x19;
        """
    )

    # Define worksheet data row style. 
style_data_row = xlwt.easyxf("""
        align:
        wrap on,
        vert center,
        horiz left;
        font:
        name Arial,
        bold off,
        height 0XA0;
        borders:
        left THIN,
        right THIN,
        top THIN,
        bottom THIN;
        """
    )

    # Define worksheet data row style. 
style_data_row_cost = xlwt.easyxf("""
        align:
        wrap on,
        vert center,
        horiz right;
        font:
        name Arial,
        bold off,
        height 0XA0;
        borders:
        left THIN,
        right THIN,
        top THIN,
        bottom THIN;
        """
    )

    # Define worksheet data row style. 
style_footer_row = xlwt.easyxf("""
        align:
        wrap on,
        vert center,
        horiz center;
        font:
        name Arial,
        bold on,
        height 0XA0;
        borders:
        left THIN,
        right THIN,
        top THIN,
        bottom THIN;
        """
    )

    # Define worksheet data row style. 
style_footer_row_cost = xlwt.easyxf("""
        align:
        wrap on,
        vert center,
        horiz right;
        font:
        name Arial,
        bold on,
        height 0XA0;
        borders:
        left THIN,
        right THIN,
        top THIN,
        bottom THIN;
        """
    )

# Define a green color style.
style_green = xlwt.easyxf(" pattern: fore-colour 0x11, pattern solid;")

# Define a red color style.
style_red = xlwt.easyxf(" pattern: fore-colour 0x0A, pattern solid;")

@login_required(login_url='/login/')
def download(request,plan_ID):
    response = HttpResponse(content_type='application/vnd.ms-excel') 
    response['Content-Disposition'] = 'attachment;filename=viewOptimized.xls'
    work_book = xlwt.Workbook(encoding = 'utf-8') 
    work_sheet = work_book.add_sheet(u'plan details')
    detail = ProductionPlan.objects.filter(id=plan_ID).values()
    for x in detail:
        total_hiring_cost = 0
        total_firing_cost = 0
        total_holding_cost = 0

        demands = []
        hiring_costs = []
        firing_costs = []
        holding_costs = []

        worker_numbers = [0]
        months = ['Start']
        for month in range(1, 13):
            demand = x[f'demand{month}'] - (x['numPermanent'] * x['prodPermanent'])
            if month == 1:
                demand -= x['inventoryInitial']
            if demand < 0:
                demand = 0
            demands.append(demand)
            
            hC = x[f'hiredTemporary{month}'] * x['costHiring']
            fC = x[f'firedTemporary{month}'] * x['costFiring']
            if month == 12:
                ihc = x['costHoldingUnit'] * x['inventoryFinal']
            else:
                ihc = x['costHoldingUnit'] * x[f'inventoryMonth{month}']
            
            hiring_costs.append(hC)
            firing_costs.append(fC)
            holding_costs.append(ihc)

            total_hiring_cost += hC
            total_firing_cost += fC
            total_holding_cost += ihc
            
            worker_numbers.append(x[f'numberTemporary{month}'])
            months.append(f'Month {month}')

    work_sheet.write(0,0, 'MONTH', style_head_row) 
    work_sheet.write(0,1, 'DEMAND', style_head_row) 
    work_sheet.write(0,2, 'REMAINING DEMAND', style_head_row) 
    work_sheet.write(0,3, 'ENDING INVENTORY UNITS', style_head_row) 
    work_sheet.write(0,4, 'NUMBER OF TEMPORARY WORKER HIRED', style_head_row) 
    work_sheet.write(0,5, 'NUMBER OF TEMPORARY WORKER FIRED', style_head_row) 
    work_sheet.write(0,6, 'NET NUMBER OF TEMPORARY WORKERS', style_head_row) 
    work_sheet.write(0,7, 'HIRING COST', style_head_row) 
    work_sheet.write(0,8, 'FIRING COST', style_head_row) 
    work_sheet.write(0,9, 'INVENTORY HOLDING COST', style_head_row)

    work_sheet.write(1,0, '1', style_data_row) 
    work_sheet.write(1,1, x['demand1'], style_data_row) 
    work_sheet.write(1,2, demands[0], style_data_row) 
    work_sheet.write(1,3, x['inventoryMonth1'], style_data_row) 
    work_sheet.write(1,4, x['hiredTemporary1'], style_data_row) 
    work_sheet.write(1,5, x['firedTemporary1'], style_data_row) 
    work_sheet.write(1,6, x['numberTemporary1'], style_data_row) 
    work_sheet.write(1,7, hiring_costs[0], style_data_row_cost) 
    work_sheet.write(1,8, firing_costs[0], style_data_row_cost) 
    work_sheet.write(1,9, holding_costs[0], style_data_row_cost)

    work_sheet.write(2,0, '2', style_data_row) 
    work_sheet.write(2,1, x['demand2'], style_data_row) 
    work_sheet.write(2,2, demands[1], style_data_row) 
    work_sheet.write(2,3, x['inventoryMonth2'], style_data_row) 
    work_sheet.write(2,4, x['hiredTemporary2'], style_data_row) 
    work_sheet.write(2,5, x['firedTemporary2'], style_data_row) 
    work_sheet.write(2,6, x['numberTemporary2'], style_data_row) 
    work_sheet.write(2,7, hiring_costs[1], style_data_row_cost) 
    work_sheet.write(2,8, firing_costs[1], style_data_row_cost) 
    work_sheet.write(2,9, holding_costs[1], style_data_row_cost)

    work_sheet.write(3,0, '3', style_data_row) 
    work_sheet.write(3,1, x['demand3'], style_data_row) 
    work_sheet.write(3,2, demands[2], style_data_row) 
    work_sheet.write(3,3, x['inventoryMonth3'], style_data_row) 
    work_sheet.write(3,4, x['hiredTemporary3'], style_data_row) 
    work_sheet.write(3,5, x['firedTemporary3'], style_data_row) 
    work_sheet.write(3,6, x['numberTemporary3'], style_data_row) 
    work_sheet.write(3,7, hiring_costs[2], style_data_row_cost) 
    work_sheet.write(3,8, firing_costs[2], style_data_row_cost) 
    work_sheet.write(3,9, holding_costs[2], style_data_row_cost)

    work_sheet.write(4,0, '4', style_data_row) 
    work_sheet.write(4,1, x['demand4'], style_data_row) 
    work_sheet.write(4,2, demands[3], style_data_row) 
    work_sheet.write(4,3, x['inventoryMonth4'], style_data_row) 
    work_sheet.write(4,4, x['hiredTemporary4'], style_data_row) 
    work_sheet.write(4,5, x['firedTemporary4'], style_data_row) 
    work_sheet.write(4,6, x['numberTemporary4'], style_data_row) 
    work_sheet.write(4,7, hiring_costs[3], style_data_row_cost) 
    work_sheet.write(4,8, firing_costs[3], style_data_row_cost) 
    work_sheet.write(4,9, holding_costs[3], style_data_row_cost)

    work_sheet.write(5,0, '5', style_data_row) 
    work_sheet.write(5,1, x['demand5'], style_data_row) 
    work_sheet.write(5,2, demands[4], style_data_row) 
    work_sheet.write(5,3, x['inventoryMonth5'], style_data_row) 
    work_sheet.write(5,4, x['hiredTemporary5'], style_data_row) 
    work_sheet.write(5,5, x['firedTemporary5'], style_data_row) 
    work_sheet.write(5,6, x['numberTemporary5'], style_data_row) 
    work_sheet.write(5,7, hiring_costs[4], style_data_row_cost) 
    work_sheet.write(5,8, firing_costs[4], style_data_row_cost) 
    work_sheet.write(5,9, holding_costs[4], style_data_row_cost)

    work_sheet.write(6,0, '6', style_data_row) 
    work_sheet.write(6,1, x['demand6'], style_data_row) 
    work_sheet.write(6,2, demands[5], style_data_row) 
    work_sheet.write(6,3, x['inventoryMonth6'], style_data_row) 
    work_sheet.write(6,4, x['hiredTemporary6'], style_data_row) 
    work_sheet.write(6,5, x['firedTemporary6'], style_data_row) 
    work_sheet.write(6,6, x['numberTemporary6'], style_data_row) 
    work_sheet.write(6,7, hiring_costs[5], style_data_row_cost) 
    work_sheet.write(6,8, firing_costs[5], style_data_row_cost) 
    work_sheet.write(6,9, holding_costs[5], style_data_row_cost)

    work_sheet.write(7,0, '7', style_data_row) 
    work_sheet.write(7,1, x['demand7'], style_data_row) 
    work_sheet.write(7,2, demands[6], style_data_row) 
    work_sheet.write(7,3, x['inventoryMonth7'], style_data_row) 
    work_sheet.write(7,4, x['hiredTemporary7'], style_data_row) 
    work_sheet.write(7,5, x['firedTemporary7'], style_data_row) 
    work_sheet.write(7,6, x['numberTemporary7'], style_data_row) 
    work_sheet.write(7,7, hiring_costs[6], style_data_row_cost) 
    work_sheet.write(7,8, firing_costs[6], style_data_row_cost) 
    work_sheet.write(7,9, holding_costs[6], style_data_row_cost)

    work_sheet.write(8,0, '8', style_data_row) 
    work_sheet.write(8,1, x['demand8'], style_data_row) 
    work_sheet.write(8,2, demands[7], style_data_row) 
    work_sheet.write(8,3, x['inventoryMonth8'], style_data_row) 
    work_sheet.write(8,4, x['hiredTemporary8'], style_data_row) 
    work_sheet.write(8,5, x['firedTemporary8'], style_data_row) 
    work_sheet.write(8,6, x['numberTemporary8'], style_data_row) 
    work_sheet.write(8,7, hiring_costs[7], style_data_row_cost) 
    work_sheet.write(8,8, firing_costs[7], style_data_row_cost) 
    work_sheet.write(8,9, holding_costs[7], style_data_row_cost)

    work_sheet.write(9,0, '9', style_data_row) 
    work_sheet.write(9,1, x['demand9'], style_data_row) 
    work_sheet.write(9,2, demands[8], style_data_row) 
    work_sheet.write(9,3, x['inventoryMonth9'], style_data_row) 
    work_sheet.write(9,4, x['hiredTemporary9'], style_data_row) 
    work_sheet.write(9,5, x['firedTemporary9'], style_data_row) 
    work_sheet.write(9,6, x['numberTemporary9'], style_data_row) 
    work_sheet.write(9,7, hiring_costs[8], style_data_row_cost) 
    work_sheet.write(9,8, firing_costs[8], style_data_row_cost) 
    work_sheet.write(9,9, holding_costs[8], style_data_row_cost)

    work_sheet.write(10,0, '10', style_data_row) 
    work_sheet.write(10,1, x['demand10'], style_data_row) 
    work_sheet.write(10,2, demands[9], style_data_row) 
    work_sheet.write(10,3, x['inventoryMonth10'], style_data_row) 
    work_sheet.write(10,4, x['hiredTemporary10'], style_data_row) 
    work_sheet.write(10,5, x['firedTemporary10'], style_data_row) 
    work_sheet.write(10,6, x['numberTemporary10'], style_data_row) 
    work_sheet.write(10,7, hiring_costs[9], style_data_row_cost) 
    work_sheet.write(10,8, firing_costs[9], style_data_row_cost) 
    work_sheet.write(10,9, holding_costs[9], style_data_row_cost)

    work_sheet.write(11,0, '11', style_data_row) 
    work_sheet.write(11,1, x['demand11'], style_data_row) 
    work_sheet.write(11,2, demands[10], style_data_row) 
    work_sheet.write(11,3, x['inventoryMonth11'], style_data_row) 
    work_sheet.write(11,4, x['hiredTemporary11'], style_data_row) 
    work_sheet.write(11,5, x['firedTemporary11'], style_data_row) 
    work_sheet.write(11,6, x['numberTemporary11'], style_data_row) 
    work_sheet.write(11,7, hiring_costs[10], style_data_row_cost) 
    work_sheet.write(11,8, firing_costs[10], style_data_row_cost) 
    work_sheet.write(11,9, holding_costs[10], style_data_row_cost)
    
    work_sheet.write(12,0, '12', style_data_row) 
    work_sheet.write(12,1, x['demand12'], style_data_row) 
    work_sheet.write(12,2, demands[11], style_data_row) 
    work_sheet.write(12,3, x['inventoryFinal'], style_data_row) 
    work_sheet.write(12,4, x['hiredTemporary12'], style_data_row) 
    work_sheet.write(12,5, x['firedTemporary12'], style_data_row) 
    work_sheet.write(12,6, x['numberTemporary12'], style_data_row) 
    work_sheet.write(12,7, hiring_costs[11], style_data_row_cost) 
    work_sheet.write(12,8, firing_costs[11], style_data_row_cost) 
    work_sheet.write(12,9, holding_costs[11], style_data_row_cost)

    work_sheet.write_merge(13,13,0,6, 'TOTAL INDIVIDUAL COSTS',style_footer_row)
    work_sheet.write(13,7, total_hiring_cost,style_footer_row_cost)
    work_sheet.write(13,8, total_firing_cost,style_footer_row_cost)
    work_sheet.write(13,9, total_holding_cost,style_footer_row_cost)

    work_sheet.write_merge(14,14,0,6,"OPTIMIZED FINAL COST FOR MULTI-PERIOD PLANNING",style_footer_row)
    work_sheet.write_merge(14,14,7,9,x['optimalCost'],style_footer_row)

    output = BytesIO()
    work_book.save(output)
    output.seek(0)
    response.write(output.getvalue()) 

    return response

@login_required(login_url='/login/')
def feedback(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject=form.cleaned_data['subject']
            content=form.cleaned_data['content']
            send_mail(subject, content , settings.EMAIL_HOST_USER, [settings.RECIPIENT_ADDRESS], True)
            return redirect ("home")
    form = ContactForm()
    context = {'form': form}
    return render(request, 'main/feedback.html', context)

@login_required(login_url='/login/')
def create_user(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        # Create a new user instance but do not save it yet
        user = User(
            first_name=first_name, 
            last_name=last_name, 
            username=username, 
            email=email
        )
        # Set the password (this will handle hashing)
        user.set_password(password)
        # Save the user to the database
        user.save()
        return redirect("read")
    return render(request, "main/users/create.html")

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Create a new user instance but do not save it yet
        user = User(
            first_name=first_name, 
            last_name=last_name, 
            username=username, 
            email=email
        )
        # Set the password (this will handle hashing)
        user.set_password(password)
        # Save the user to the database
        user.save()
        
        return redirect("login")
    
    return render(request, "main/signup.html")

@login_required(login_url='/login/')
def read_user(request):
    # pk = request.user.id
    # user = User.objects.get(id=pk)
    userData = User.objects.all().values
    return render(request, 'main/users/read.html', {'userData': userData})

@login_required(login_url='/login/')
def update_user(request, id):
    # pk = request.user.id
    userData = User.objects.get(id=id)
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        is_active = request.POST.get("is_active")
        is_staff = request.POST.get("is_staff")
        is_superuser = request.POST.get("is_superuser")
        userData.first_name = first_name
        userData.last_name = last_name
        userData.username = username
        userData.email = email
        userData.is_active = (is_active == 'on')
        userData.is_staff = (is_staff == 'on')
        userData.is_superuser = (is_superuser == 'on')
        userData.save()
        return redirect("read")
    return render(request, "main/users/update.html", {"userData": userData})

@login_required(login_url='/login/')
def editprofile(request, id):
    # pk = request.user.id
    userData = User.objects.get(id=id)
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        userData.first_name = first_name
        userData.last_name = last_name
        userData.username = username
        userData.save()
        return redirect("/")
    return render(request, "main/editprofile.html", {"userData": userData})

@login_required(login_url='/login/')
def delete_user(request, id):
    # pk = request.user.id
    userData = User.objects.get(id=id)
    userData.delete()
    return redirect("read")