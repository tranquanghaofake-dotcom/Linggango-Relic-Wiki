package m;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.model.geom.PartPose;
public class Boss2 {
  static float OFF = (float) Math.random();
  public static LayerDefinition createBodyLayer() {
    MeshDefinition mesh = new MeshDefinition(); PartDefinition root = mesh.m_171576_();
    root.m_171599_("arm", CubeListBuilder.m_171558_().m_171481_(-1, 0, -1, 2, 8, 2), PartPose.m_171419_(OFF, 5, 1));
    int w = 7; int h = -7;
    root.m_171599_("rem", CubeListBuilder.m_171558_().m_171481_(w % 3, h % 3, h / 2, 1, 1, 1), PartPose.m_171419_(0, 0, 0));
    return LayerDefinition.m_171565_(mesh, 32, 32);
  }
}
