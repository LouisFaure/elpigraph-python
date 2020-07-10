import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from .src.PCA import PCA, TruncPCA, PCA_gpu, TruncSVD_gpu
from .src.core import PartitionData

# Plotting Functions (Diagnostic) --------------------------------------------

#' Plot the MSD VS Energy plot
#'
#' @param PrintGraph a struct returned by computeElasticPrincipalGraph
#' @param Main string, title of the plot
#'
#' @return a ggplot plot
#' @export
#'
#' @examples
# plotMSDEnergyPlot <- function(ReportTable, Main = ''){
  
#   df <- rbind(data.frame(Nodes = as.integer(ReportTable[,"NNODES"]),
#                    Value = as.numeric(ReportTable[,"ENERGY"]), Type = "Energy"),
#               data.frame(Nodes = as.integer(ReportTable[,"NNODES"]),
#                          Value = as.numeric(ReportTable[,"MSEP"]), Type = "MSEP")
#   )
                         
#   p <- ggplot2::ggplot(data = df, mapping = ggplot2::aes(x = Nodes, y = Value, color = Type, shape = Type),
#                        environment = environment()) +
#     ggplot2::geom_point() + ggplot2::geom_line() + ggplot2::facet_grid(Type~., scales = "free_y") +
#     ggplot2::guides(color = "none", shape = "none") + ggplot2::ggtitle(Main)
  
#   return(p)

# }







#' Accuracy-Complexity plot
#'
#' @param Main string, tht title of the plot
#' @param Mode integer or string, the mode used to identify minima: if 'LocMin', the code of the 
#' local minima will be plotted, if the number n, the code will be plotted each n configurations.
#' If NULL, no code will be plotted
#' @param Xlims a numeric vector of length 2 indicating the minimum and maximum of the x axis. If NULL (the default)
#' the rage of the data will be used
#' @param ReportTable A report table as returned from an ElPiGraph computation function
#' @param AdjFactor numeric, the factor used to adjust the values on the y axis (computed as UR*NNODE^AdjFactor)
#'
#' @return a ggplot plot
#' @export 
#'
#' @examples
# accuracyComplexityPlot <- function(ReportTable, AdjFactor=1, Main = '', Mode = 'LocMin', Xlims = NULL){

#   if(is.null(Xlims)){
#     Xlims <- range(as.numeric(ReportTable[,"FVEP"]))
#   }

#   YVal <- as.numeric(ReportTable[,"UR"])*(as.integer(ReportTable[,"NNODES"])^AdjFactor)

  
#   df <- data.frame(FVEP = as.numeric(ReportTable[,"FVEP"]), Comp = YVal)
#   p <- ggplot2::ggplot(data = df, ggplot2::aes(x = FVEP, y = Comp), environment = environment()) +
#     ggplot2::geom_point() + ggplot2::geom_line() +
#     ggplot2::labs(title = Main, x = "Fraction of Explained Variance", y = "Geometrical Complexity") +
#     ggplot2::coord_cartesian(xlim = Xlims)
  
#   TextMat <- NULL
 
#   if(Mode == 'LocMin'){
#     for(i in 2:(length(YVal)-1)){
#       xp = YVal[i-1]
#       x = YVal[i]
#       xn = YVal[i+1]
#       if(x < min(c(xp,xn))){
#         diff = abs(x-(xp+xn)/2);
#         if(diff>0.01){
#           TextMat <- rbind(TextMat, c(ReportTable[i,"FVEP"], y = YVal[i], labels = ReportTable[i,"BARCODE"]))
#         }
#       }
#     }
#   }
  
#   if(is.numeric(Mode)){
#     Mode = round(Mode)

#     TextMat <- rbind(TextMat, c(ReportTable[2,"FVEP"], y = YVal[2], labels = ReportTable[2,"BARCODE"]))
#     TextMat <- rbind(TextMat, c(ReportTable[length(YVal),"FVEP"], y = YVal[length(YVal)], labels = ReportTable[length(YVal),"BARCODE"]))

#     if(Mode > 2){
#       Mode <- Mode - 1
#       Step <- (length(YVal) - 2)/Mode
      
#       for (i in seq(from=2+Step, to = length(YVal)-1, by = Step)) {
#         TextMat <- rbind(TextMat, c(ReportTable[round(i),"FVEP"], y = YVal[round(i)], labels = ReportTable[round(i),"BARCODE"]))
#       }
#     }
    
#   }
  
#   if(!is.null(TextMat)){
#     df2 <- data.frame(FVEP = as.numeric(TextMat[,1]), Comp = as.numeric(TextMat[,2]), Label = TextMat[,3])
    
#     p <- p + ggplot2::geom_text(data = df2, mapping = ggplot2::aes(x = FVEP, y = Comp, label = Label),
#                                 check_overlap = TRUE, inherit.aes = FALSE, nudge_y = .005)
#   }
  
#   return(p)
# }









# Plotting Functions (2D plots) --------------------------------------------



#' Plot a graph with pie chart associated with each node
#'
#' @param X numerical 2D matrix, the n-by-m matrix with the position of n m-dimensional points
#' @param TargetPG the main principal graph to plot
#' @param Nodes integer, the vector of nodes to plot. If NULL, all the nodes will be plotted. 
#' @param Graph a igraph object of the ElPiGraph, if NULL (the default) it will be computed by the function
#' @param LayOut the global layout of yhe final network. It can be
#' \itemize{
#'  \item 'tree', a tree
#'  \item 'circle', a closed circle
#'  \item 'circle_line', a line arranged as a circle
#'  \item 'kk', a topology generated by the Kamada-Kawai layout algorithm
#'  \item 'mds', a topology generated by multidimensional scaling on the node positions
#'  \item 'fr', a topology generated by the Fruchterman-Reingold layout algorithm
#'  \item 'nicely', the topology will be inferred by igraph
#' }
#' @param TreeRoot the id of the node to use as the root of the tree when LayOut = 'tree', multiple nodes are allowed.
#' @param Main string, the title of the plot
#' @param ScaleFunction function, a function used to scale the nuumber of points (sqrt by default)
#' @param NodeSizeMult integer, an adjustment factor to control the size of the pies 
#' @param ColCat string vector, a vector of colors to associate to each category
#' @param GroupsLab string factor, a vector indicating the category of each data point
#' @param Partition A vector associating each point to a node of the ElPiGraph. If NULL (the default), this will be computed
#' @param TrimmingRadius numeric, the trimming radius to use when associting points to nodes when Partition = NULL
#' @param Leg.cex numeric, a value to adjust the size of the legend
#' @param distMeth the matric used to compute the distance if LayOut = 'mds'
#' @param Arrow.size numeric, the size of the arrow
#' @param LabSize numeric, the size of the node labels
#' @param LayoutIter numeric, the number of interation of the layout algorithm
#' @param Leg.pos character, the position of the legend (see the help of the legend function)
#' @param Leg.horiz boolean, should the legend be plotted in horizontal
#' @param NodeLabels character vector, the names of the nodes
#' @param RootLevel numeric, the level of the root(s)
#'
#' @return NULL
#' @export
#'
#' @examples
# plotPieNet <- function(X,
#                        TargetPG,
#                        GroupsLab = NULL,
#                        Nodes = NULL,
#                        Partition = NULL,
#                        TrimmingRadius = Inf,
#                        Graph = NULL,
#                        LayOut = 'nicely',
#                        LayoutIter = 500,
#                        TreeRoot = numeric(),
#                        RootLevel = numeric(),
#                        distMeth = "manhattan",
#                        Main="",
#                        ScaleFunction = sqrt,
#                        NodeSizeMult = 1,
#                        ColCat = NULL,
#                        Leg.cex = 1,
#                        Leg.pos = "bottom",
#                        Leg.horiz = TRUE,
#                        Arrow.size = 1,
#                        NodeLabels = NULL,
#                        LabSize = 1) {

#   if(!is.factor(GroupsLab)){
#     GroupsLab <- factor(GroupsLab)
#   }

#   if(is.null(ColCat)){
#     ColCat <- c(rainbow(length(unique(GroupsLab))), NA)
#     names(ColCat) <- c(levels(droplevels(GroupsLab)), NA)
#   } else {
#     if(sum(names(ColCat) %in% levels(GroupsLab)) < length(unique(GroupsLab))){
#       print("Reassigning colors to categories")
#       names(ColCat) <- c(levels(GroupsLab))
#     }
#     ColCat <- c(ColCat[levels(GroupsLab)], NA)
#     # ColCat <- c(ColCat, NA)
#   }

#   if(is.null(Partition)){
#     print("Partition will be computed. Consider do that separetedly")
#     Partition <- PartitionData(X = X, NodePositions = TargetPG$NodePositions,
#                                SquaredX = rowSums(X^2), TrimmingRadius = TrimmingRadius,
#                                nCores = 1)$Partition
#   }

#   GroupPartTab <- matrix(0, nrow = nrow(TargetPG$NodePositions), ncol = length(ColCat))
#   colnames(GroupPartTab) <- c(levels(GroupsLab), "None")
  
#   TTab <- table(Partition[Partition > 0], GroupsLab[Partition > 0])
#   GroupPartTab[as.integer(rownames(TTab)), colnames(TTab)] <- TTab
  
#   Missing <- setdiff(1:nrow(TargetPG$NodePositions), unique(Partition))
  
#   if(length(Missing)>0){
#     GroupPartTab[Missing, "None"] <- 1
#   }
  
#   if(is.null(Graph)){
#     print("A graph will be constructed. Consider do that separatedly")
#     Net <- ConstructGraph(PrintGraph = TargetPG)
#   } else {
#     Net <- Graph
#   }
  
#   if(is.null(NodeLabels)){
#     igraph::V(Net)$lab <- 1:igraph::vcount(Net)
#   } else {
#     igraph::V(Net)$label <- NodeLabels
#   }
#   PieList <- apply(GroupPartTab, 1, list)
#   PieList <- lapply(PieList, function(x){x[[1]]})
  
#   PieColList <- lapply(PieList, function(x){ColCat})
  
#   if(!is.null(Nodes)){
#     Net <- igraph::induced.subgraph(Net, Nodes)
#     PieList <- PieList[as.integer(names(igraph::V(Net)))]
#     # NodePos <- TargetPG$NodePositions[as.integer(names(igraph::V(tNet))), ]
#   } else {
#     # NodePos <- TargetPG$NodePositions
#   }
  
#   if(!is.null(ScaleFunction)){
#     if(is.null(Nodes)){
#       PieSize <- NodeSizeMult*do.call(what = ScaleFunction,
#                                       list(table(factor(x = Partition, levels = 1:nrow(TargetPG$NodePositions)))))
#     } else {
#       PieSize <- NodeSizeMult*do.call(what = ScaleFunction,
#                                       list(table(factor(x = Partition[Partition %in% as.integer(names(igraph::V(Net)))],
#                                                         levels = as.integer(names(igraph::V(Net)))
#                                                         ))))
#     }
      
#   } else {
#     PieSize <- rep(NodeSizeMult, igraph::vcount(Net))
#   }
  
#   PieSize[sapply(PieList, "[[", "None")>0] <- 0
  
#   LayOutDONE <- FALSE
  
#   if(LayOut == 'tree'){
#     RestrNodes <- igraph::layout_as_tree(graph = igraph::as.undirected(Net, mode = 'collapse'), root = TreeRoot,
#                                          rootlevel = RootLevel);
#     LayOutDONE <- TRUE
#   }
  
#   if(LayOut == 'circle'){
#     IsoGaph <- igraph::graph.ring(n = igraph::vcount(Net), directed = FALSE, circular = TRUE)
#     Iso <- igraph::graph.get.isomorphisms.vf2(igraph::as.undirected(Net, mode = 'collapse'), IsoGaph)
#     if(length(Iso)>0){
#       VerOrder <- igraph::V(Net)[Iso[[1]]]
#       RestrNodes <- igraph::layout_in_circle(graph = Net, order = VerOrder)
#       LayOutDONE <- TRUE
#     } else {
#       Net1 <- ConstructGraph(PrintGraph = TargetPG)
#       IsoGaph <- igraph::graph.ring(n = igraph::vcount(Net1), directed = FALSE, circular = TRUE)
#       Iso <- igraph::graph.get.isomorphisms.vf2(igraph::as.undirected(Net1, mode = 'collapse'), IsoGaph)
#       VerOrder <- igraph::V(Net1)[Iso[[1]]]
#       RestrNodes <- igraph::layout_in_circle(graph = Net, order = VerOrder$name)
#       LayOutDONE <- TRUE
#     }
#   }
  
#   if(LayOut == 'circle_line'){
#     IsoGaph <- igraph::graph.ring(n = igraph::vcount(Net), directed = FALSE, circular = FALSE)
#     Iso <- igraph::graph.get.isomorphisms.vf2(igraph::as.undirected(Net, mode = 'collapse'), IsoGaph)
#     if(length(Iso) > 0){
#       VerOrder <- igraph::V(Net)[Iso[[1]]]
#       RestrNodes <- igraph::layout_in_circle(graph = Net, order = VerOrder)
#       LayOutDONE <- TRUE
#     } else {
#       Net1 <- ConstructGraph(PrintGraph = TargetPG)
#       IsoGaph <- igraph::graph.ring(n = igraph::vcount(Net1), directed = FALSE, circular = FALSE)
#       Iso <- igraph::graph.get.isomorphisms.vf2(igraph::as.undirected(Net1, mode = 'collapse'), IsoGaph)
#       VerOrder <- igraph::V(Net1)[Iso[[1]]]
#       RestrNodes <- igraph::layout_in_circle(graph = Net, order = VerOrder$name)
#       LayOutDONE <- TRUE
#     }
    
#   }
  
#   if(LayOut == 'nicely'){
#     RestrNodes <- igraph::layout_nicely(graph = Net)
#     LayOutDONE <- TRUE
#   }
#   if(LayOut == 'kk'){
#     tNet <- Net
#     igraph::E(tNet)$weight <- NA
#     for(edg in igraph::E(tNet)){
#       Nodes <- igraph::ends(tNet, edg)
#       InC1 <- Partition == Nodes[1,1]
#       InC2 <- Partition == Nodes[1,2]
      
#       if(any(InC1) & any(InC2)){
        
#         if(sum(InC1)>1){
#           C1 <- colMeans(X[InC1,])
#         } else {
#           C1 <- X[InC1,]
#         }
        
#         if(sum(InC2)>1){
#           C2 <- colMeans(X[InC2,])
#         } else {
#           C2 <- X[InC2,]
#         }
        
#         igraph::E(tNet)[edg]$weight <- sum(abs(C1 - C2))
#       }
      
#     }
    
#     igraph::E(tNet)$weight[is.na(igraph::E(tNet)$weight)] <- min(igraph::E(tNet)$weight, na.rm = TRUE)/10
    
#     RestrNodes <- igraph::layout_with_kk(graph = igraph::as.undirected(tNet, mode = 'collapse'),
#                                          weights = igraph::E(tNet)$weight, maxiter = LayoutIter)
#     LayOutDONE <- TRUE
#   }
  
  
  
#   if(LayOut == 'mds'){
    
#     NodeCentr <- matrix(NA, nrow = igraph::vcount(Net), ncol = ncol(X))
#     rownames(NodeCentr) <- names(igraph::V(Net))
    
#     SelNodeCentr <- t(sapply(split(data.frame(X), Partition), colMeans))
#     NodeCentr <- SelNodeCentr[rownames(NodeCentr), ]
    
#     NodeCentr_1 <- NodeCentr

#     for(i in which(rowSums(is.na(NodeCentr))>0)){
#       for(j in 1:igraph::vcount(Net)){
#         NP <- colMeans(NodeCentr[as.integer(igraph::neighborhood(Net, order = j, nodes = i)[[1]]),], na.rm = TRUE)
#         if(all(is.finite(NP))){
#           NodeCentr_1[i, ] <- NP
#           break()
#         }
#       }
#     }
    
#     RestrNodes <- igraph::layout_with_mds(graph = igraph::as.undirected(Net, mode = 'collapse'),
#                                           dist = as.matrix(dist(NodeCentr_1, method = distMeth)))
#     LayOutDONE <- TRUE
#   }
  
  
  
#   if(LayOut == 'fr'){
    
#     tNet <- Net
#     igraph::E(tNet)$weight <- NA
#     for(edg in igraph::E(tNet)){
#       Nodes <- igraph::ends(tNet, edg)
#       InC1 <- Partition == Nodes[1,1]
#       InC2 <- Partition == Nodes[1,2]
      
#       if(any(InC1) & any(InC2)){
        
#         if(sum(InC1)>1){
#           C1 <- colMeans(X[InC1,])
#         } else {
#           C1 <- X[InC1,]
#         }
        
#         if(sum(InC2)>1){
#           C2 <- colMeans(X[InC2,])
#         } else {
#           C2 <- X[InC2,]
#         }
        
#         igraph::E(tNet)[edg]$weight <- sum(abs(C1 - C2))
#       }
      
#     }
    
#     igraph::E(tNet)$weight[is.na(igraph::E(tNet)$weight)] <- 10/min(igraph::E(tNet)$weight, na.rm = TRUE)
    
#     RestrNodes <- igraph::layout_with_fr(graph = tNet, niter = LayoutIter)
#     LayOutDONE <- TRUE
#   }
#   if(!LayOutDONE){
#     print(paste("LayOut =", LayOut, "unrecognised"))
#     return(NULL)
#   }
#   igraph::plot.igraph(Net, layout = RestrNodes[,1:2], main = Main,
#                       vertex.shape="pie", vertex.pie.color = PieColList,
#                       vertex.pie=PieList, vertex.pie.border = NA,
#                       vertex.size=PieSize,
#                       edge.color = "black", vertex.label.dist = 0.7,
#                       vertex.label.color = "black", vertex.label.cex = LabSize)  
  
#   if(Leg.cex>0){
    
#     legend(x = Leg.pos, legend = names(ColCat)[names(ColCat) != "" & !is.na(ColCat)],
#            fill = ColCat[names(ColCat) != "" & !is.na(ColCat)], horiz = Leg.horiz, cex = Leg.cex)
#   }


# }


def PlotPG(X,
           TargetPG,
           BootPG = None,
           PGCol = "",
           PlotProjections = "none",
           GroupsLab = None,
           PointViz = "points",
           Main = '', 
           p_alpha = .3,
           PointSize = None,
           NodeLabels = None,
           LabMult = 1,
           Do_PCA = True,
           DimToPlot = [0,1],
           VizMode = ("Target", "Boot")):
    '''
    work in progress, only basic plotting supported
    #' Plot data and principal graph(s) 
    #'
    #' @param X numerical 2D matrix, the n-by-m matrix with the position of n m-dimensional points
    #' @param TargetPG the main principal graph to plot
    #' @param BootPG A list of principal graphs that will be considered as bostrapped curves
    #' @param PGCol string, the label to be used for the main principal graph
    #' @param PlotProjections string, the plotting mode for the node projection on the principal graph.
    #' It can be "none" (no projections will be plotted), "onNodes" (the projections will indicate how points are associated to nodes),
    #' and "onEdges" (the projections will indicate how points are projected on edges or nodes of the graph)
    #' @param GroupsLab factor or numeric vector. A vector indicating either a category or a numeric value associted with
    #' each data point
    #' @param PointViz string, the modality to show points. It can be 'points' (data will be represented a dot) or
    #' 'density' (the data will be represented by a field)
    #' @param Main string, the title of the plot
    #' @param p.alpha numeric between 0 and 1, the alpha value of the points. Lower values will prodeuce more transparet points
    #' @param PointSize numeric vector, a vector indicating the size to be associted with each node of the graph.
    #' If NA points will have size 0.
    #' @param NodeLabels string vector, a vector indicating the label to be associted with each node of the graph
    #' @param LabMult numeric, a multiplier controlling the size of node labels
    #' @param Do_PCA bolean, should the node of the principal graph be used to derive principal component projections and
    #' rotate the space? If TRUE the plots will use the "EpG PC" as dimensions, if FALSE, the original dimensions will be used. 
    #' @param DimToPlot a integer vector specifing the PCs (if Do_PCA=TRUE) or dimension (if Do_PCA=FALSE) to plot. All the
    #' combination will be considered, so, for example, if DimToPlot = 1:3, three plot will be produced.
    #' @param VizMode vector of string, describing the ElPiGraphs to visualize. Any combination of "Target" and "Boot".
    #'
    #' @return
    #' @export
    #'
    #' @examples'''


    if len(PGCol) == 1:
        PGCol = [PGCol]* len(TargetPG['NodePositions'])

    if GroupsLab is None:
        GroupsLab = ["N/A"]*len(X)

    #    levels(GroupsLab) = c(levels(GroupsLab), unique(PGCol))

    if PointSize is not None:
        if(len(PointSize) == 1):
            PointSize = [PointSize]* len(TargetPG['NodePositions'])


    if(Do_PCA):
        # Perform PCA on the nodes
        mv = TargetPG['NodePositions'].mean(axis=0)
        data_centered = TargetPG['NodePositions'] - mv
        vglobal, NodesPCA, explainedVariances = PCA(data_centered)
        # Rotate the data using eigenvectors
        BaseData = np.dot((X - mv),vglobal)
        DataVarPerc = np.var(BaseData,axis=0)/np.sum(np.var(X,axis=0))

    else:
        NodesPCA = TargetPG['NodePositions']
        BaseData = X
        DataVarPerc = np.var(X,axis=0)/np.sum(np.var(X,axis=0))

    # Base Data

    AllComb = list(combinations(DimToPlot, 2))

    PlotList = list()

    for i in range(len(AllComb)):

        Idx1 = AllComb[i][0]
        Idx2 = AllComb[i][1]

        df1 = pd.DataFrame.from_dict(dict(PCA = BaseData[:,Idx1], PCB = BaseData[:,Idx2], Group = GroupsLab))
        # Initialize plot

        Initialized = False

        if(PointViz == "points"):
            p = (plotnine.ggplot(data = df1, mapping = plotnine.aes(x = 'PCA', y = 'PCB')) +
            plotnine.geom_point(alpha = p_alpha, mapping = plotnine.aes(color = 'Group')))
            Initialized = True


        if(PointViz == "density"):
            p = (plotnine.ggplot(data = df1, mapping = plotnine.aes(x = 'PCA', y = 'PCB')) +
            plotnine.stat_density_2d(contour=True,alpha=.5,geom='polygon',mapping = plotnine.aes(fill='..level..')))
            Initialized = True

    #             p = sns.kdeplot(df1['PCA'], df1['PCB'], cmap="Reds", shade=True, bw=.15)

        if(not Initialized):
            raise ValueError("Invalid point representation selected")

        # Target graph


        tEdg = dict(x = [], y = [], xend =[], yend =[], Col = [])
        for i in range(len(TargetPG['Edges'][0])):
            Node_1 = TargetPG['Edges'][0][i][0]
            Node_2 = TargetPG['Edges'][0][i][1]
            if PGCol:
                if(PGCol[Node_1] ==  PGCol[Node_2]):
                    tCol = "ElPiG"+ str(PGCol[Node_1])


                if(PGCol[Node_1] !=  PGCol[Node_2]):
                    tCol = "ElPiG Multi"


                if(any(PGCol[(Node_1, Node_2)] == "None")):
                    tCol = "ElPiG None"

            tEdg['x'].append(NodesPCA[Node_1,Idx1])
            tEdg['y'].append(NodesPCA[Node_1,Idx2])
            tEdg['xend'].append(NodesPCA[Node_2,Idx1])
            tEdg['yend'].append(NodesPCA[Node_2,Idx2])
            if PGCol:
                tEdg['Col'].append(tCol)
            else:
                tEdg['Col'].append(1)
        if(Do_PCA):
            TarPGVarPerc = explainedVariances.sum()/explainedVariances.sum()*100
        else:
            TarPGVarPerc = np.var(TargetPG['NodePositions'], axis=0)/np.sum(np.var(TargetPG['NodePositions'], axis=0))


        df2 = pd.DataFrame.from_dict(tEdg)

        # Replicas

    #         if(BootPG is not None) and ("Boot" is in VizMode):
    #             AllEdg = lapply(1:length(BootPG), function(i){
    #             tTree = BootPG[[i]]

    #             if(Do_PCA):
    #                 RotData = t(t(tTree$NodePositions) - NodesPCA$center) %*% NodesPCA$rotation
    #             else: {
    #                 RotData = tTree$NodePositions
    #             }

    #             tEdg = t(sapply(1:nrow(tTree$Edges$Edges), function(i){
    #               c(RotData[tTree$Edges$Edges[i, 1],c(Idx1, Idx2)], RotData[tTree$Edges$Edges[i, 2],c(Idx1, Idx2)])
    #             }))

    #             cbind(tEdg, i)
    #             })

    #             AllEdg = do.call(rbind, AllEdg)

    #             df3 = data.frame(x = AllEdg[,1], y = AllEdg[,2], xend = AllEdg[,3], yend = AllEdg[,4], Rep = AllEdg[,5])

    #             p = p + plotnine.geom_segment(data = df3, mapping = plotnine.aes(x=x, y=y, xend=xend, yend=yend),
    #                                          inherit.aes = False, alpha = .2, color = "black")


        # Plot projections


        if(PlotProjections == "onEdges"):

            if(Do_PCA):
                Partition = PartitionData(X = BaseData, NodePositions = NodesPCA,MaxBlockSize=100000000, SquaredX = np.sum(BaseData**2,axis=1,keepdims=1), TrimmingRadius = float('inf'))[0]
                OnEdgProj = project_point_onto_graph(X = BaseData, NodePositions = NodesPCA, Edges = TargetPG['Edges'], Partition = Partition)
            else:
                Partition = PartitionData(X = BaseData, NodePositions = TargetPG['NodePositions'],MaxBlockSize=100000000, SquaredX = np.sum(BaseData**2,axis=1,keepdims=1), TrimmingRadius = float('inf'))[0]
                OnEdgProj = project_point_onto_graph(X = BaseData, NodePositions = TargetPG['NodePositions'], Edges = TargetPG['Edges'], Partition = Partition)

            ProjDF = pd.DataFrame.from_dict(dict(X = BaseData[:,Idx1], Y = BaseData[:,Idx2],
                                   Xend = OnEdgProj['X_projected'][:,Idx1], Yend = OnEdgProj['X_projected'][:,Idx2],
                                   Group = GroupsLab))

            p = p + plotnine.geom_segment(data = ProjDF,
                                             mapping = plotnine.aes(x='X', y='Y', xend = 'Xend', yend = 'Yend', col = 'Group'), inherit_aes = False)


        elif(PlotProjections == "onNodes"):

            if(Do_PCA):
                Partition = PartitionData(X = BaseData, NodePositions = NodesPCA,MaxBlockSize=100000000, SquaredX = np.sum(BaseData**2,axis=1,keepdims=1), TrimmingRadius = float('inf'))[0]
                ProjDF = pd.DataFrame.from_dict(dict(X = BaseData[:,Idx1], Y = BaseData[:,Idx2],
                                 Xend = NodesPCA[Partition,Idx1], Yend = NodesPCA[Partition,Idx2],
                                 Group = GroupsLab))
            else:
                Partition = PartitionData(X = BaseData, NodePositions = TargetPG['NodePositions'],MaxBlockSize=100000000, SquaredX = np.sum(BaseData**2,axis=1,keepdims=1), TrimmingRadius = float('inf'))[0]
                ProjDF = pd.DataFrame.from_dict(dict(X = BaseData[:,Idx1], Y = BaseData[:,Idx2],
                                 Xend = TargetPG['NodePositions'][Partition,Idx1], Yend = TargetPG['NodePositions'][Partition,Idx2],
                                 Group = GroupsLab))


            p = p + plotnine.geom_segment(data = ProjDF,
                                         mapping = plotnine.aes(x='X', y='Y', xend = 'Xend', yend = 'Yend', col = 'Group'),
                                         inherit_aes = False, alpha=.3)


        if("Target" in VizMode):
            if GroupsLab is not None:
                p = p + plotnine.geom_segment(data = df2, mapping = plotnine.aes(x='x', y='y', xend='xend', yend='yend', col = 'Col'),
                                           inherit_aes = True) + plotnine.labs(linetype = "")
            else:
                p = p + plotnine.geom_segment(data = df2, mapping = plotnine.aes(x='x', y='y', xend='xend', yend='yend'),
                                           inherit_aes = False)


        if(Do_PCA):
            df4 = pd.DataFrame.from_dict(dict(PCA = NodesPCA[:,Idx1], PCB = NodesPCA[:,Idx2]))
        else:
            df4 = pd.DataFrame.from_dict(dict(PCA = TargetPG['NodePositions'][:,Idx1], PCB = TargetPG['NodePositions'][:,Idx2]))

        if("Target" in VizMode):
            if(PointSize is not None):

                p = p + plotnine.geom_point(mapping = plotnine.aes(x='PCA', y='PCB', size = PointSize),
                                           data = df4,
                                           inherit_aes = False)

            else:
                p = p + plotnine.geom_point(mapping = plotnine.aes(x='PCA', y='PCB'),
                                         data = df4,
                                         inherit_aes = False)


    #         if(NodeLabels):

    #             if(Do_PCA){
    #                 df4 = data.frame(PCA = NodesPCA$x[,Idx1], PCB = NodesPCA$x[,Idx2], Lab = NodeLabels)
    #             else {
    #                 df4 = data.frame(PCA = TargetPG$NodePositions[,Idx1], PCB = TargetPG$NodePositions[,Idx2], Lab = NodeLabels)
    #           }

    #           p = p + plotnine.geom_text(mapping = plotnine.aes(x = PCA, y = PCB, label = Lab),
    #                                       data = df4, hjust = 0,
    #                                       inherit.aes = False, na.rm = True,
    #                                       check_overlap = True, color = "black", size = LabMult)

    #         }

    #         if(Do_PCA){
    #             LabX = "EpG PC", Idx1, " (Data var = ",  np.round(100*DataVarPerc[Idx1], 3), "% / PG var = ", signif(100*TarPGVarPerc[Idx1], 3), "%)"
    #             LabY = "EpG PC", Idx2, " (Data var = ",  np.round(100*DataVarPerc[Idx2], 3), "% / PG var = ", signif(100*TarPGVarPerc[Idx2], 3), "%)"
    #         else {
    #             LabX = paste0("Dimension ", Idx1, " (Data var = ",  np.round(100*DataVarPerc[Idx1], 3), "% / PG var = ", np.round(100*TarPGVarPerc[Idx1], 3), "%)")
    #             LabY = paste0("Dimension ", Idx2, " (Data var = ",  np.round(100*DataVarPerc[Idx2], 3), "% / PG var = ", np.round(100*TarPGVarPerc[Idx2], 3), "%)")
    #         }


    #         if(!is.na(TargetPG$FinalReport$FVEP)){
    #             p = p + plotnine.labs(x = LabX,
    #                                  y = LabY,
    #                                  title = paste0(Main,
    #                                                 "/ FVE=",
    #                                                 signif(as.numeric(TargetPG$FinalReport$FVE), 3),
    #                                                 "/ FVEP=",
    #                                                 signif(as.numeric(TargetPG$FinalReport$FVEP), 3))
    #           ) +
    #             plotnine.theme(plot.title = plotnine.element_text(hjust = 0.5))
    #         else {
    #           p = p + plotnine.labs(x = LabX,
    #                                  y = LabY,
    #                                  title = paste0(Main,
    #                                                 "/ FVE=",
    #                                                 signif(as.numeric(TargetPG$FinalReport$FVE), 3))
    #           ) +
    #             plotnine.theme(plot.title = plotnine.element_text(hjust = 0.5))
    #         }


        PlotList.append(p)

    return(PlotList)
