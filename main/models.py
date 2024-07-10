from django.db import models
from django.contrib.auth.models import User

class ProductionPlan(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)                                                 # Plan Name
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    length = models.IntegerField()                                                          # Plan Length
    filled = models.BooleanField(default=False)                                             # Input Made?
    
    # Input
    demand1 = models.IntegerField(default=0)			                                    # Demand for Month 1
    demand2 = models.IntegerField(default=0)			                                    # Demand for Month 2
    demand3 = models.IntegerField(default=0)			                                    # Demand for Month 3
    demand4 = models.IntegerField(default=0)			                                    # Demand for Month 4
    demand5 = models.IntegerField(default=0)			                                    # Demand for Month 5
    demand6 = models.IntegerField(default=0)			                                    # Demand for Month 6
    demand7 = models.IntegerField(default=0)			                                    # Demand for Month 7
    demand8 = models.IntegerField(default=0)			                                    # Demand for Month 8
    demand9 = models.IntegerField(default=0)			                                    # Demand for Month 9
    demand10 = models.IntegerField(default=0)			                                    # Demand for Month 10
    demand11 = models.IntegerField(default=0)			                                    # Demand for Month 11
    demand12 = models.IntegerField(default=0)			                                    # Demand for Month 12
    numPermanent = models.IntegerField(default=0)		                                    # Number of Permanent Worker(s)
    prodPermanent = models.IntegerField(default=0)		                                    # Production of a Permanent Worker
    prodTemporary = models.IntegerField(default=0)		                                    # Production of a Temporary Worker
    costHiring = models.DecimalField(max_digits=19, decimal_places=2, default=0)			# Temporary Worker Hiring Cost
    costFiring = models.DecimalField(max_digits=19, decimal_places=2, default=0)			# Temporary Worker Firing Cost
    costHoldingUnit = models.DecimalField(max_digits=19, decimal_places=2, default=0)		# Monthly Holding Cost per Unit
    inventoryInitial = models.IntegerField(default=0)	                                    # Initial Inventory Level
    inventoryFinal = models.IntegerField(default=0)		                                    # Final Inventory Level / Ending Inventory for Month 12
    
    # Optimized Output
    inventoryMonth1 = models.IntegerField(default=0)                                        # Ending Inventory for Month 1
    inventoryMonth2 = models.IntegerField(default=0)                                        # Ending Inventory for Month 2
    inventoryMonth3 = models.IntegerField(default=0)                                        # Ending Inventory for Month 3
    inventoryMonth4 = models.IntegerField(default=0)                                        # Ending Inventory for Month 4
    inventoryMonth5 = models.IntegerField(default=0)                                        # Ending Inventory for Month 5
    inventoryMonth6 = models.IntegerField(default=0)                                        # Ending Inventory for Month 6
    inventoryMonth7 = models.IntegerField(default=0)                                        # Ending Inventory for Month 7
    inventoryMonth8 = models.IntegerField(default=0)                                        # Ending Inventory for Month 8
    inventoryMonth9 = models.IntegerField(default=0)                                        # Ending Inventory for Month 9
    inventoryMonth10 = models.IntegerField(default=0)                                       # Ending Inventory for Month 10
    inventoryMonth11 = models.IntegerField(default=0)                                       # Ending Inventory for Month 11
    hiredTemporary1 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 1
    hiredTemporary2 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 2
    hiredTemporary3 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 3
    hiredTemporary4 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 4
    hiredTemporary5 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 5
    hiredTemporary6 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 6
    hiredTemporary7 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 7
    hiredTemporary8 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 8
    hiredTemporary9 = models.IntegerField(default=0)                                        # Number of Temporary Worker Hired for Month 9
    hiredTemporary10 = models.IntegerField(default=0)                                       # Number of Temporary Worker Hired for Month 10
    hiredTemporary11 = models.IntegerField(default=0)                                       # Number of Temporary Worker Hired for Month 11
    hiredTemporary12 = models.IntegerField(default=0)                                       # Number of Temporary Worker Hired for Month 12
    firedTemporary1 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 1
    firedTemporary2 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 2
    firedTemporary3 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 3
    firedTemporary4 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 4
    firedTemporary5 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 5
    firedTemporary6 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 6
    firedTemporary7 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 7
    firedTemporary8 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 8
    firedTemporary9 = models.IntegerField(default=0)                                        # Number of Temporary Worker Fired for Month 9
    firedTemporary10 = models.IntegerField(default=0)                                       # Number of Temporary Worker Fired for Month 10
    firedTemporary11 = models.IntegerField(default=0)                                       # Number of Temporary Worker Fired for Month 11
    firedTemporary12 = models.IntegerField(default=0)                                       # Number of Temporary Worker Fired for Month 12
    numberTemporary1 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 1
    numberTemporary2 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 2
    numberTemporary3 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 3
    numberTemporary4 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 4
    numberTemporary5 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 5
    numberTemporary6 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 6
    numberTemporary7 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 7
    numberTemporary8 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 8
    numberTemporary9 = models.IntegerField(default=0)                                       # Number of Temporary Worker for Month 9
    numberTemporary10 = models.IntegerField(default=0)                                      # Number of Temporary Worker for Month 10
    numberTemporary11 = models.IntegerField(default=0)                                      # Number of Temporary Worker for Month 11
    numberTemporary12 = models.IntegerField(default=0)                                      # Number of Temporary Worker for Month 12
    optimalCost = models.DecimalField(max_digits=19, decimal_places=2, default=0)           # Optimized Cost for Multi-Period Planning 